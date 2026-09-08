import runpy
from ml.salary_forecast.model.salary_predictor import SalaryPredictor

__all__ = ["SalaryPredictor"]

if __name__ == "__main__":
    #执行SalaryPredictor
    runpy.run_module(
        #指定模块路径
        "ml.salary_forecast.model.salary_predictor",
        run_name="__main__",
    )