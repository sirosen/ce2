#!/usr/bin/env python3

import calendar
import datetime
import statistics

import boto3

ce = boto3.client("ce")
now = datetime.datetime.now()


def days_this_month():
    return calendar.monthrange(now.year, now.month)[1]


def start_of_month_from_yesterday():
    return (now - datetime.timedelta(days=1)).strftime("%Y-%m-01")


def today():
    return now.strftime("%Y-%m-%d")


def tomorrow():
    return (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def start_of_next_month():
    next_month = now.replace(day=28) + datetime.timedelta(days=4)
    return next_month.strftime("%Y-%m-01")


def safe_variance(lst):
    if len(lst) < 2:
        return "N/A"
    return round(statistics.variance(lst), 2)


def get_month_to_date():
    raw = ce.get_cost_and_usage(
        TimePeriod=dict(Start=start_of_month_from_yesterday(), End=today()),
        Granularity="DAILY",
        Metrics=["AmortizedCost"],
        GroupBy=[dict(Type="DIMENSION", Key="SERVICE")],
    )
    results = raw["ResultsByTime"]
    service_metric_map = {}

    for metric in ("AmortizedCost",):
        cur = service_metric_map[metric] = {}

        for r in results:
            for g in r["Groups"]:
                service = g["Keys"][0]
                val = round(float(g["Metrics"][metric]["Amount"]), 2)
                if service not in cur:
                    cur[service] = []
                cur[service].append(val)
    return service_metric_map


def get_forecast():
    if (now + datetime.timedelta(days=1)).month != now.month:
        return ("N/A", "N/A", "N/A")

    raw = ce.get_cost_forecast(
        TimePeriod=dict(Start=tomorrow(), End=start_of_next_month()),
        Granularity="MONTHLY",
        Metric="AMORTIZED_COST",
        PredictionIntervalLevel=80,
    )
    results = raw["ForecastResultsByTime"]
    r = results[0]
    return (
        r["MeanValue"],
        r["PredictionIntervalLowerBound"],
        r["PredictionIntervalUpperBound"],
    )


def main():
    print("Per Service Report")
    metric_map = get_month_to_date()
    amcosts = list(metric_map["AmortizedCost"].items())
    amcosts = sorted(amcosts, key=lambda x: sum(x[1]), reverse=True)
    amcosts = [(x, y) for (x, y) in amcosts if sum(y) > 0.0]

    max_name_width = max(len(x) for x, y in amcosts)
    cols = ("Est. Monthly", "Running Total", "Average", "Variance", "Yesterday")
    cols = [(x, len(x)) for x in cols]
    print(
        "{} || {} | {} | {} | {} | {}".format(
            "Service".ljust(max_name_width),
            cols[0][0],
            cols[1][0],
            cols[2][0],
            cols[3][0],
            cols[4][0],
        )
    )
    print("---------")
    for service, vals in amcosts:
        mean = round(statistics.mean(vals), 2)
        print(
            "{} || {} | {} | {} | {} | {}".format(
                service.ljust(max_name_width),
                str(round(days_this_month() * mean, 2)).ljust(cols[0][1]),
                str(round(sum(vals), 2)).ljust(cols[1][1]),
                str(mean).ljust(cols[2][1]),
                str(safe_variance(vals)).ljust(cols[3][1]),
                str(vals[-1]).ljust(cols[4][1]),
            )
        )
    print()

    forecast, forecast_lower, forecast_upper = get_forecast()
    print("Account Forecast")
    print("Monthly Total: {}".format(forecast))
    print("  Lower Bound: {}".format(forecast_lower))
    print("  Upper Bound: {}".format(forecast_upper))


if __name__ == "__main__":
    main()
