"""Explicit fixture timing shared by independently executed collectors."""
import time
PHASES = dict(spark_startup_s=0.0, warmup_s=0.0, cleanup_s=0.0)

def start_session(builder):
    started = time.perf_counter()
    spark = builder.getOrCreate()
    PHASES['spark_startup_s'] += time.perf_counter()-started
    try:
        started = time.perf_counter()
        spark.range(32).selectExpr('sum(id)').collect()
        PHASES['warmup_s'] += time.perf_counter()-started
    except BaseException:
        spark.stop()
        raise
    return spark

def stop_session(spark):
    started = time.perf_counter()
    try:
        spark.stop()
    finally:
        PHASES['cleanup_s'] += time.perf_counter()-started
