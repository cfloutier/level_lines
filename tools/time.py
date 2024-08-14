from datetime import timedelta


def td_format(td_object: timedelta):
    seconds = int(td_object.total_seconds())
    if seconds <= 1:
        return f"{seconds}.{td_object.microseconds/10000:2.0f} ms"
    periods = [
        ('y',        60*60*24*365),
        ('m',       60*60*24*30),
        ('d',         60*60*24),
        ('h',        60*60),
        ('m',      60),
        ('s',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
           
            strings.append("%s %s" % (period_value, period_name))

    return " ".join(strings)


print(td_format(timedelta(seconds=1.2)))