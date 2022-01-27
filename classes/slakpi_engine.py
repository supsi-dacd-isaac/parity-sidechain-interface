from classes.pm_sidechain_interface import PMSidechainInterface


class SlaKpiManager(PMSidechainInterface):
    """
    SlaKpiManager class
    """
    def __init__(self, cfg, logger):
        """
        Constructor
        :param cfg: configuration dictionary
        :type dict
        :param logger
        :type Logger
        """
        super().__init__(cfg, logger)

    def get_kpi_features(self, idx, ts_start, ts_end):
        kpi_info = self.handle_get('/kpi/%s_%i-%s' % (idx, ts_start, ts_end))
        return kpi_info

    def get_kpi_value(self, idx, account_name, ts_start, ts_end):
        kpi_info = self.handle_get('/kpiMeasure/%s-%s_%i-%s-%i' % (account_name, idx, ts_start, ts_end, ts_end))
        return kpi_info

    @staticmethod
    def check_value(kpi_feature, kpi_dataset):
        if kpi_feature['rule'] == 'gt':
            if kpi_dataset['value'] > kpi_feature['limit']:
                return kpi_feature['penalty']

        if kpi_feature['rule'] == 'lt':
            if kpi_dataset['value'] < kpi_feature['limit']:
                return kpi_feature['penalty']

        return 0
