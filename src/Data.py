import pandas as pd
import numpy as np
from datetime import timedelta

#const
CUTOFF_DATE = pd.to_datetime("2021-09-09")
LOOKAHEAD_DAYS = 365

#подготавливаю данные для обучения модели
def prepare_training_dataset(clients_path: str, defaults_path: str) -> pd.DataFrame:

    clients = pd.read_csv(clients_path, parse_dates=['ReportDate'])
    defaults = pd.read_csv(defaults_path, parse_dates=['DefaultDate'])

    #привожу к нижнему регистру колонки
    clients.rename(columns={"INN": "inn", "ReportDate": "reportdate"}, inplace=True)
    defaults.rename(columns={"INN": "inn", "DefaultDate": "default_date"}, inplace=True)

    #получаю минимальный дефолт до cutoff
    defaults = defaults[defaults["default_date"] <= CUTOFF_DATE]
    earliest_default = defaults.groupby("inn")["default_date"].min().reset_index()

    #мердж с другой таблицей
    df = clients.merge(earliest_default, on="inn", how="left")

    #убираю наблюдения, по которым не прошло 365 дней
    df = df[df["reportdate"] <= CUTOFF_DATE - timedelta(days=LOOKAHEAD_DAYS)]

    #флаг дефолта
    df["default_flag"] = np.where(
        (df["default_date"].notna()) &
        (df["default_date"] > df["reportdate"]) &
        (df["default_date"] <= df["reportdate"] + timedelta(days=LOOKAHEAD_DAYS)),
        1, 0
    )

    #оставляю только первое дефолтное наблюдение на клиента
    def_rows = df[df["default_flag"] == 1].sort_values(["inn", "reportdate"]).drop_duplicates("inn")
    non_def_rows = df[df["default_flag"] == 0]

    #получаю финальную выборку
    final = pd.concat([def_rows, non_def_rows], ignore_index=True)
    final = final[["inn", "reportdate", "1110", "1150", "2110", "default_flag"]]

    return final


if __name__ == "__main__":
    df = prepare_training_dataset("data/clients_data.csv", "data/defaults_data.csv")
    df.to_csv("data/processed_dataset.csv", index=False)
