from time import time
import logging

class RunsConfig(object):
    """ General configuration parameters for runs """
    def __init__(self,
                 number_of_data_points = None,
                 min_runtime           = None):
        self._number_of_data_points = number_of_data_points
        self._min_runtime           = min_runtime
    
    @property
    def number_of_data_points(self):
        return self._number_of_data_points
        
    @property
    def min_runtime(self):
        return self._min_runtime
        
    def combined(self, runDef):
        config = RunsConfig(self._number_of_data_points, self._min_runtime)
        val = runDef.get('number_of_data_points', None)
        if val:
            config._number_of_data_points = val
        val = runDef.get('min_runtime', None)
        if val:
            config._min_runtime = val
        return config
    
    def log(self):
        msg = "Run Config: number of data points: %d" % (self._number_of_data_points)
        if self._min_runtime:
            msg += ", min_runtime: %dms" % (self._min_runtime)
        logging.debug(msg)
    
    def create_termination_check(self, bench_cfg):
        return TerminationCheck(self, bench_cfg)

class QuickRunsConfig(RunsConfig):
    
    def __init__(self, number_of_data_points = None,
                       min_runtime           = None,
                       max_time              = None):
        super(QuickRunsConfig, self).__init__(number_of_data_points,
                                              min_runtime)
        self._max_time = max_time
    
    def combined(self, runDef):
        """For Quick runs, only the global config is taken into account.""" 
        return self
    
    @property
    def max_time(self):
        return self._max_time
    
    def create_termination_check(self, bench_cfg):
        return QuickTerminationCheck(self, bench_cfg)

class TerminationCheck(object):
    def __init__(self, run_cfg, bench_cfg):
        self._run_cfg   = run_cfg
        self._bench_cfg = bench_cfg
    
    def should_terminate(self, number_of_data_points):
        if number_of_data_points >= self._run_cfg.number_of_data_points:
            logging.debug("Reached number_of_data_points for %s" % (self._bench_cfg.name))
            return True
        else:
            return False

class QuickTerminationCheck(TerminationCheck):
    def __init__(self, run_cfg, bench_cfg):
        super(QuickTerminationCheck, self).__init__(run_cfg, bench_cfg)
        self._start_time = time()
    
    def should_terminate(self, number_of_data_points):
        if time() - self._start_time > self._run_cfg.max_time:
            logging.debug("Maximum runtime is reached for %s" % (self._run_cfg.name))
            return True
        return super(QuickTerminationCheck, self).should_terminate(number_of_data_points)
