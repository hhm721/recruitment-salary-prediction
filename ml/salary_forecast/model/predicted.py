import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from ml.salary_forecast.config.config import Config
from ml.salary_forecast.utils.feature_engineer import FeatureEngineer
import warnings
warnings.filterwarnings('ignore')

class Predicted:

    def __init__(self, X_test, y_test, feature_names=None):
        self.X_test = X_test
        self.y_test = y_test
        self.models = {}
        self.model_keys = Config.MODEL_KEYS
        self.feature_names = feature_names

    def validate_all_models(self, model_keys=None, save_report=True):
        """批量验证四个模型（目标均为高低薪平均值）"""
        if model_keys is None:
            model_keys = list(self.model_keys)

        print(f"\n{'=' * 60}\n批量验证\n{'=' * 60}")
        X, y, extra = self.resolve_validation_xy()
        results = {}
        summary_rows = []
        for model_key in model_keys:
            model_path = os.path.join(Config.MODEL_SAVE_PATH, f'{model_key}_model.pkl')
            in_memory = isinstance(self.models, dict) and model_key in self.models
            if not in_memory and not os.path.exists(model_path):
                print(f'跳过 {model_key}: 模型不存在')
                continue
            try:
                report = self.validate_model(
                    model_key, X=X, y=y, extra=extra, save_report=save_report
                )
                results[model_key] = report
                m = report['metrics_salary']
                summary_rows.append({
                    '模型': model_key,
                    '判定': report['judgment']['status'],
                    'R2': round(m['r2'], 4),
                    'MAE': round(m['mae'], 2),
                    'RMSE': round(m['rmse'], 2),
                    '相对误差%': round(m['relative_error'], 2),
                    '±20%命中': round(m['accuracy_20'], 1),
                })
            except Exception as e:
                print(f'验证 {model_key} 失败: {e}')
                results[model_key] = {'error': str(e), 'judgment': {'status': 'fail'}}

        summary_df = pd.DataFrame(summary_rows)
        print(f"\n{'=' * 60}\n验证汇总（对比高低薪平均值）\n{'=' * 60}")
        if len(summary_df) > 0:
            print(summary_df.to_string(index=False))

        statuses = [r.get('judgment', {}).get('status') for r in results.values()]
        statuses = [s for s in statuses if s]
        if statuses and all(s == 'pass' for s in statuses):
            final_message = '全部模型验证通过：对高低薪平均值预测合理'
            all_passed = True
        elif statuses and all(s in ('pass', 'warn') for s in statuses):
            final_message = '全部模型基本通过，可继续优化'
            all_passed = False
        elif any(s == 'pass' for s in statuses):
            final_message = '部分模型通过，其余未达标'
            all_passed = False
        else:
            final_message = ('验证未通过,请确认训练目标为 salary_target')
            all_passed = False

        print(f'\n最终结论: {final_message}')
        return {
            'final_message': final_message,
            'all_passed': all_passed,
            'summary': summary_df,
            'results': results,
        }

    def resolve_validation_xy(self, X=None, y=None, extra=None):
        """
        解析验证数据：优先使用调用方传入或实例内与训练同源的 X_test/y_test
        """
        if X is not None and y is not None:
            y_arr = np.asarray(y, dtype=float).ravel()
            if float(np.nanmax(y_arr)) < 20:
                raise ValueError('传入的 y 疑似对数薪资，验证须使用高低薪平均值 salary_target')
            return np.asarray(X, dtype=float), y_arr, extra or {}

        # 训练同会话：直接用实例测试集（与模型 Scaler 一致，最可靠）
        if (
                self.X_test is not None and self.y_test is not None
                and len(np.asarray(self.y_test).ravel()) > 0
                and float(np.nanmax(np.asarray(self.y_test, dtype=float))) >= 20
        ):
            print('使用实例内测试集验证')
            return (
                np.asarray(self.X_test, dtype=float),
                np.asarray(self.y_test, dtype=float).ravel(),
                {'source': 'instance_X_test', 'target_col': 'salary_target'},
            )
        X_loaded, y_loaded, extra_loaded = self.load_validation_dataset()
        extra_loaded['source'] = extra_loaded.get('path', 'validation_data.csv')
        return X_loaded, y_loaded, extra_loaded

    def validate_model(self, model_key, X=None, y=None, extra=None, model=None, save_report=True):
        """
        验证单个模型是否合理拟合 salary_target=(最低+最高)/2
        """
        print(f"{'=' * 50}\n验证模型: {model_key}\n\n{'=' * 50}")
        X, y_true, extra = self.resolve_validation_xy(X, y, extra)

        if model is None:
            # 【修改】仅当 models 为 dict 且包含该 key 时才走内存模型
            # 原先 models 是 list 时：'xgboost' in list 为 True，随后 list['xgboost'] 报错
            if isinstance(self.models, dict) and model_key in self.models:
                model = self.models[model_key]
                print(f'使用内存中已训练模型: {model_key}')
            else:
                model, save_meta = self.load_saved_model(model_key)
                # 【修改】加载后缓存到 models dict，供后续复用
                if isinstance(self.models, dict):
                    self.models[model_key] = model
                print(f'已加载磁盘模型: {model_key}_model.pkl')
                if save_meta.get('metrics'):
                    print(f"训练记录指标: {save_meta['metrics']}")

        y_pred = self.predict_salary(model, X)
        metrics = self.evaluate_salary_target(
            y_pred,
            y_true,
            salary_min=extra.get('salary_min'),
            salary_max=extra.get('salary_max'),
        )
        judgment = self.judge_salary_validation(metrics)

        print(
            f"主指标 R2={metrics['r2']:.4f} | "
            f"MAE={metrics['mae']:.2f} | RMSE={metrics['rmse']:.2f} | "
            f"相对误差={metrics['relative_error']:.2f}% | "
            f"±20%命中={metrics['accuracy_20']:.1f}%"
        )
        if metrics.get('within_range_rate') is not None:
            print(f"补充指标 落入[最低,最高]比例: {metrics['within_range_rate']:.1f}%")
        print(f"判定: 【{judgment['status']}】{judgment['message']}")

        preview = []
        for i in range(min(10, len(y_true))):
            true_v = float(y_true[i])
            pred_v = float(y_pred[i])
            abs_err = abs(true_v - pred_v)
            rel_err = abs_err / true_v * 100 if true_v != 0 else 0.0
            row = {
                '真实平均值': round(true_v, 2),
                '预测平均值': round(pred_v, 2),
                '绝对误差': round(abs_err, 2),
                '相对误差%': round(rel_err, 2),
            }
            if extra.get('salary_min') is not None:
                smin = float(extra['salary_min'][i])
                smax = float(extra['salary_max'][i])
                row['最低'] = round(smin, 2)
                row['最高'] = round(smax, 2)
                row['是否落在区间'] = bool(smin <= pred_v <= smax)
            preview.append(row)

        preview_df = pd.DataFrame(preview)
        print('\n样本对比（前10条，标签=高低薪平均值）')
        print(preview_df.to_string(index=True))

        report = {
            'model_key': model_key,
            'validated_at': datetime.now().isoformat(),
            'target_definition': '(salary_min + salary_max) / 2',
            'data_info': {
                'source': extra.get('source', 'validation_data.csv'),
                'path': extra.get('path', Config.DATA_SAVE_PATH),
                'n_samples': int(len(y_true)),
                'n_features': int(X.shape[1]),
                'target_type': 'salary_target_mean',
                'salary_range': [float(np.min(y_true)), float(np.max(y_true))],
            },
            'metrics_salary': metrics,
            'judgment': judgment,
            'preview': preview,
        }

        if save_report:
            os.makedirs(Config.MODEL_SAVE_PATH, exist_ok=True)
            report_path = os.path.join(
                Config.MODEL_SAVE_PATH, f'validation_report_{model_key}.json'
            )
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=float)
            print(f'验证报告已保存 -> {report_path}')

        return report

    def save_validation_dataset(self, salary_min=None, salary_max=None):
        """
        保存验证集。y必须是 salary_target = (最低薪+最高薪)/2
        """
        os.makedirs(os.path.dirname(Config.DATA_SAVE_PATH), exist_ok=True)
        if self.X_test is None or self.y_test is None:
            raise ValueError('实例中没有 X_test/y_test，无法保存验证集')

        n_features = int(np.asarray(self.X_test).shape[1])
        if not self.feature_names or len(self.feature_names) != n_features:
            raise ValueError(
                f'保存验证集需要与特征列数一致的 feature_names'
                f'(当前 names={None if self.feature_names is None else len(self.feature_names)}, '
                f'X列数={n_features})。请传入训练时的 feature_names'
            )

        if isinstance(self.X_test, np.ndarray):
            X_test_df = pd.DataFrame(self.X_test, columns=list(self.feature_names))
        else:
            X_test_df = self.X_test.copy()
            if list(X_test_df.columns) != list(self.feature_names):
                if X_test_df.shape[1] != len(self.feature_names):
                    raise ValueError('X_test 列数与 feature_names 不一致')
                X_test_df = pd.DataFrame(
                    np.asarray(X_test_df, dtype=float),
                    columns=list(self.feature_names),
                )

        y_arr = np.asarray(self.y_test, dtype=float).ravel()
        if float(np.nanmax(y_arr)) < 20:
            raise ValueError(f'验证标签疑似为对数薪资（max={float(np.nanmax(y_arr)):.4f} < 20）')

        # 主标签：区间中点（与训练目标一致）；兼容列名 salary
        payload = {
            'salary_target': y_arr,
            'salary': y_arr,
        }
        if salary_min is not None and salary_max is not None:
            payload['salary_min'] = np.asarray(salary_min, dtype=float).ravel()
            payload['salary_max'] = np.asarray(salary_max, dtype=float).ravel()

        label_df = pd.DataFrame(payload)
        validation_df = pd.concat(
            [X_test_df.reset_index(drop=True), label_df.reset_index(drop=True)],
            axis=1,
        )
        validation_df.to_csv(Config.DATA_SAVE_PATH, index=False)

        meta = {
            'path': Config.DATA_SAVE_PATH,
            'n_samples': len(validation_df),
            'n_features': int(X_test_df.shape[1]),
            'target_definition': '(salary_min + salary_max) / 2',
            'target_column': 'salary_target',
            'salary_target_min': float(np.min(y_arr)),
            'salary_target_max': float(np.max(y_arr)),
            'salary_target_mean': float(np.mean(y_arr)),
            'has_salary_range': salary_min is not None and salary_max is not None,
            'created_at': datetime.now().isoformat(),
        }
        meta_path = os.path.join(Config.BASE_DIR, 'data', 'validation_data_meta.json')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"验证集已保存: {len(validation_df)} 条 -> {Config.DATA_SAVE_PATH}")
        print(f"目标值: salary_target = (最低薪 + 最高薪) / 2")
        print(
            f"中点薪资范围: {meta['salary_target_min']:.0f} ~ "
            f"{meta['salary_target_max']:.0f}，均值: {meta['salary_target_mean']:.0f}"
        )

    def prepare_validation_dataset(self, test_size=0.2, random_state=42):
        """
        按与训练相同流程构建验证集
        """
        print(f"{'=' * 50}\n准备验证集\n{'=' * 50}")
        fe = FeatureEngineer()
        df_processed, feature_names = fe.data_partition()

        if 'salary_target' not in df_processed.columns:
            raise ValueError('缺少 salary_target，请确认特征工程已计算 (min+max)/2')

        X = df_processed[feature_names].values
        y = df_processed['salary_target'].values.astype(float)
        has_range = (
                'salary_min_parsed' in df_processed.columns
                and 'salary_max_parsed' in df_processed.columns
        )

        if len(X) == 0 or len(y) == 0:
            raise ValueError('没有有效数据，无法准备验证集')
        if float(np.max(y)) < 20:
            raise ValueError('salary_target 疑似为 log，请检查特征工程')

        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X)
        indices = np.arange(len(y))

        if has_range:
            X_train, X_test, y_train, y_test, _, idx_test = train_test_split(
                X_scaled, y, indices, test_size=test_size, random_state=random_state
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=random_state
            )

        # 注意：重新 fit Scaler 会使旧模型失效，必须随后重新训练再验证
        print(
            '警告: prepare_validation_dataset 会重新 fit RobustScaler；'
            '旧模型与新验证集不匹配，请先重新训练再验证。'
        )
        joblib.dump(scaler, Config.ROBUST_SCALER_SAVE_PATH)
        print(f"RobustScaler 已保存 -> {Config.ROBUST_SCALER_SAVE_PATH}")

        self.X_test = X_test
        self.y_test = y_test
        self.feature_names = feature_names
        salary_min = salary_max = None
        if has_range:
            salary_min = df_processed['salary_min_parsed'].values[idx_test]
            salary_max = df_processed['salary_max_parsed'].values[idx_test]
        self.save_validation_dataset(salary_min=salary_min, salary_max=salary_max)
        print(f"验证集准备完成: {Config.DATA_SAVE_PATH}")
        # 【修改】predictor 应返回当前验证实例，不能返回 scaler 路径字符串
        return {
            'validation_path': Config.DATA_SAVE_PATH,
            'scaler_path': Config.ROBUST_SCALER_SAVE_PATH,
            'n_samples': len(y_test),
            'n_features': len(feature_names),
            'salary_min': float(np.min(y_test)),
            'salary_max': float(np.max(y_test)),
            'predictor': self,
        }

    def load_validation_dataset(self):
        """
        加载验证集
        """
        if not os.path.exists(Config.DATA_SAVE_PATH):
            raise FileNotFoundError(f'验证集不存在: {Config.DATA_SAVE_PATH}')

        df = pd.read_csv(Config.DATA_SAVE_PATH)
        if 'salary_target' in df.columns:
            y = df['salary_target'].values.astype(float)
            target_col = 'salary_target'
        elif 'salary' in df.columns:
            y = df['salary'].values.astype(float)
            target_col = 'salary'
        else:
            raise ValueError('验证集缺少 salary_target / salary 列')

        if float(np.max(y)) < 20:
            raise ValueError(f'验证标签疑似对数薪资（max={float(np.max(y)):.4f} < 20）')

        drop_cols = {'salary_target', 'salary', 'salary_min', 'salary_max'}
        feature_cols = [c for c in df.columns if c not in drop_cols]

        # 列名为 0,1,2... 时按列位置对齐到 feature_names
        looks_positional = (
            len(feature_cols) > 0
            and all(str(c).isdigit() for c in feature_cols)
        )
        if self.feature_names is None:
            names_path = os.path.join(Config.MODEL_SAVE_PATH, 'feature_names.json')
            if os.path.exists(names_path):
                with open(names_path, encoding='utf-8') as f:
                    self.feature_names = json.load(f)

        if self.feature_names is not None and looks_positional:
            if len(feature_cols) != len(self.feature_names):
                raise ValueError(
                    f'验证集匿名特征列数({len(feature_cols)})与 feature_names'
                    f'({len(self.feature_names)})不一致，请重新训练并保存验证集'
                )
            print('检测到匿名特征列(0,1,2...)，按训练 feature_names 列位置对齐')
            X = df[feature_cols].values.astype(float)
        elif self.feature_names is not None:
            missing = [c for c in self.feature_names if c not in df.columns]
            if missing:
                raise ValueError(f'验证集缺少特征列: {missing[:5]} ...')
            X = df[list(self.feature_names)].values.astype(float)
        else:
            X = df[feature_cols].values.astype(float)
            self.feature_names = feature_cols

        extra = {'target_col': target_col, 'path': Config.DATA_SAVE_PATH}
        if 'salary_min' in df.columns and 'salary_max' in df.columns:
            extra['salary_min'] = df['salary_min'].values.astype(float)
            extra['salary_max'] = df['salary_max'].values.astype(float)

        print(
            f"验证集已加载: {len(df)} 条, 特征={X.shape[1]}, "
            f"目标列={target_col}（高低薪平均值）, "
            f"范围={float(np.min(y)):.0f} ~ {float(np.max(y)):.0f}"
        )
        return X, y, extra

    def load_saved_model(self, model_key):
        """加载已保存模型"""
        model_path = os.path.join(Config.MODEL_SAVE_PATH, f'{model_key}_model.pkl')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f'模型文件不存在: {model_path}')
        save_data = joblib.load(model_path)
        if isinstance(save_data, dict) and 'model' in save_data:
            model = save_data['model']
            if self.feature_names is None and save_data.get('feature_names'):
                self.feature_names = save_data['feature_names']
            return model, save_data
        return save_data, {'model': save_data, 'model_key': model_key}

    def predict_salary(self, model, X):
        """输出应为高低薪平均值"""
        if isinstance(model, xgb.Booster):
            feature_names = None
            if self.feature_names is not None and len(self.feature_names) == X.shape[1]:
                feature_names = list(self.feature_names)
            dmatrix = xgb.DMatrix(X, feature_names=feature_names)
            pred = model.predict(dmatrix)
        else:
            pred = model.predict(X)
        return np.asarray(pred, dtype=float).ravel()

    def evaluate_salary_target(self, y_pred, y_true, salary_min=None, salary_max=None):
        """
        按高低薪平均值评估
        """
        y_pred = np.asarray(y_pred, dtype=float).ravel()
        y_true = np.asarray(y_true, dtype=float).ravel()
        y_pred = np.maximum(y_pred, 1.0)
        y_true = np.maximum(y_true, 1.0)

        # 若模型仍输出对数空间，给出明确错误提示
        if float(np.max(y_pred)) < 20 and float(np.max(y_true)) >= 20:
            raise ValueError(
                '模型预测值像对数薪资（max<20），但验证标签是高低薪平均值。'
                '请确认训练目标为 salary_target 而非 salary_target_log'
            )

        metrics = self.evaluate(y_pred, y_true)
        metrics['target_definition'] = '(salary_min + salary_max) / 2'

        if salary_min is not None and salary_max is not None:
            smin = np.asarray(salary_min, dtype=float).ravel()
            smax = np.asarray(salary_max, dtype=float).ravel()
            in_range = (y_pred >= smin) & (y_pred <= smax)
            metrics['within_range_rate'] = float(np.mean(in_range) * 100)
        else:
            metrics['within_range_rate'] = None

        return metrics

    def evaluate(self, y_pred, y_true):
        """评估模型性能"""
        y_pred = np.array(y_pred).flatten()
        y_true = np.array(y_true).flatten()
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        # 计算相对误差
        relative_error = np.mean(np.abs((y_true - y_pred) / (y_true + 1))) * 100
        # 计算精确度（预测在±20%内的比例）
        accuracy_20 = np.mean(np.abs((y_pred - y_true) / y_true) <= 0.2) * 100
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'relative_error': relative_error,
            'accuracy_20': accuracy_20
        }

    def judge_salary_validation(self, metrics):
        """
        基于「平均值目标」业务指标判定：
        pass: R2>=0.90 且 ±20%命中>=90% 且 相对误差<8%
        warn: R2>=0.80 且 ±20%命中>=80% 且 相对误差<15%
        """
        r2 = metrics['r2']
        acc20 = metrics['accuracy_20']
        rel = metrics['relative_error']
        thresholds = {
            'r2_pass': 0.90,
            'r2_warn': 0.80,
            'accuracy_20_pass': 90.0,
            'accuracy_20_warn': 80.0,
            'mean_rel_error_pass': 8.0,
            'mean_rel_error_warn': 15.0,
        }

        if r2 >= 0.90 and acc20 >= 90 and rel < 8:
            status, passed = 'pass', True
            message = '验证通过：对「高低薪平均值」的预测达到优秀标准'
        elif r2 >= 0.80 and acc20 >= 80 and rel < 15:
            status, passed = 'warn', False
            message = '基本通过：对平均值预测接近要求，建议继续优化'
        else:
            status, passed = 'fail', False
            message = '未通过：对「高低薪平均值」预测未达要求，请检查数据一致性或重新训练'

        return {
            'status': status,
            'passed': passed,
            'message': message,
            'thresholds': thresholds,
        }

    def validate_saved_models(self, model_keys=None, prepare_if_missing=True):
        """
        对模型做高低薪平均值验证
        """
        if not os.path.exists(Config.DATA_SAVE_PATH):
            if prepare_if_missing:
                raise FileNotFoundError(
                    f'验证集不存在: {Config.DATA_SAVE_PATH}\n'
                    '请先运行 salary_model.py 完成训练并在同会话中保存验证集；'
                    '不要单独 prepare_validation_dataset 后再用旧模型验证。'
                )
            raise FileNotFoundError(
                f'验证集不存在: {Config.DATA_SAVE_PATH}'
            )
        # 模型训练指标与当前验证结果可能因 Scaler 不一致而失真
        print('请确认 validation_data.csv 与当前模型来自同一次训练')
        return self.validate_all_models(model_keys=model_keys, save_report=True)

if __name__ == "__main__":
    pass