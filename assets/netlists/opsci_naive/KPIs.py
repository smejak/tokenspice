from enforce_typing import enforce_types
import math
from typing import List

from engine import KPIsBase
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, INF
from util.strutil import prettyBigNum

@enforce_types
class KPIs(KPIsBase.KPIsBase):

    def __init__(self, time_step: int):
        super().__init__(time_step)
                
        #for these, append a new value with each tick
        self._total_assets_per_tick: List[float] = [] # how many assets are in the marketplace
        self._n_sellers_per_tick: List[float] = []
        self._total_OCEAN_minted__per_tick: List[float] = []
        self._total_OCEAN_burned__per_tick: List[float] = []
        self._total_OCEAN_minted_USD__per_tick: List[float] = []
        self._total_OCEAN_burned_USD__per_tick: List[float] = []
        self._sellers_revenue_per_tick: List[float] = []
        self._revenue_per_seller_per_s__per_tick: List[float] = []

    def takeStep(self, state):
        super().takeStep(state) #parent e.g. increments self._tick

        # self._granttakers_revenue_per_tick__per_tick.append(
        #     state.grantTakersSpentAtTick())
        
        am = state.getAgent("marketplaces1")
        self._total_assets_per_tick.append(
            am.getTotalAssets()) #TODO: getTotalAssets()

        sellers = state.getAgent("sellers")
        self._revenue_per_seller_per_s__per_tick.append(
            sellers.revenuePerSellerPerSecond()) #TODO: revenuePerSellerPerSecond()
        self._n_sellers_per_tick.append(
            sellers.numSellers()) #TODO: NumSellers()
        self._sellers_revenue_per_tick.append(
            sellers.revenuePerTick()) #TODO: revenuePerTick()

        O_minted = state.totalOCEANminted()
        O_burned = state.totalOCEANburned()
        self._total_OCEAN_minted__per_tick.append(O_minted)
        self._total_OCEAN_burned__per_tick.append(O_burned)

        O_price = state.OCEANprice()
        O_minted_USD = O_minted * O_price
        O_burned_USD = state.totalOCEANburnedUSD()
        self._total_OCEAN_minted_USD__per_tick.append(O_minted_USD)
        self._total_OCEAN_burned_USD__per_tick.append(O_burned_USD)

    def tick(self) -> int:
        """# ticks since start of run"""
        assert len(self._revenue_per_seller_per_s__per_tick) == self._tick
        return self._tick
        
    #=======================================================================
    #revenue numbers: 1 seller
    def oneSellerMonthlyRevenueNow(self) -> float:
        t2 = self.elapsedTime()
        t1 = t2 - S_PER_MONTH
        return self._oneSellerRevenueOverInterval(t1, t2)
    
    def oneSellerAnnualRevenueNow(self) -> float:
        t2 = self.elapsedTime()
        t1 = t2 - S_PER_YEAR
        return self._oneSellerRevenueOverInterval(t1, t2)
    
    def oneSellerAnnualRevenueOneYearAgo(self) -> float:
        t2 = self.elapsedTime() - S_PER_YEAR
        t1 = t2 - S_PER_YEAR
        return self._oneSellerRevenueOverInterval(t1, t2)
            
    def _oneSellerRevenueOverInterval(self, t1: int, t2:int) -> float:
        return self._revenueOverInterval(t1, t2, self.oneSellerRevenuePerSecond)

    def oneSellerRevenuePerSecond(self, tick) -> float:
        """Returns oneSeller's revenue per second at a given tick"""
        return self._revenue_per_seller_per_s__per_tick[tick]

    #=======================================================================
    #revenue numbers: n sellers
    def allSellersMonthlyRevenueNow(self) -> float:
        t2 = self.elapsedTime()
        t1 = t2 - S_PER_MONTH
        return self._allSellersRevenueOverInterval(t1, t2)
    
    def allSellersAnnualRevenueNow(self) -> float:
        t2 = self.elapsedTime()
        t1 = t2 - S_PER_YEAR
        return self._allSellersRevenueOverInterval(t1, t2)
    
    def allSellersAnnualRevenueOneYearAgo(self) -> float:
        t2 = self.elapsedTime() - S_PER_YEAR
        t1 = t2 - S_PER_YEAR
        return self._allSellersRevenueOverInterval(t1, t2)

    def allSellersRevenuePerSecond(self, tick) -> float:
        """Returns allmkt's revenue per second at a given tick"""
        return self._revenue_per_seller_per_s__per_tick[tick] \
            * self._n_sellers_per_tick[tick]
            
    def _allSellersRevenueOverInterval(self, t1: int, t2:int) -> float:
        return self._revenueOverInterval(t1, t2, self.allSellersRevenuePerSecond)
    
    #=======================================================================
    def _revenueOverInterval(self, t1: int, t2:int, revenuePerSecondFunc) \
        -> float:
        """
        Helper function for _{onemkt, allmkts, ocean}revenueOverInterval().

        In time from t1 to t2 (both in # seconds since start), 
        how much $ was earned, using the revenuePerSecondFunc.
        """
        assert t2 > t1
        tick1: int = max(0, math.floor(t1 / self._time_step))
        tick2: int = min(self.tick(), math.floor(t2 / self._time_step) + 1) 
        rev = 0.0
        for tick_i in range(tick1, tick2):
            rev_this_s = revenuePerSecondFunc(tick_i)
            
            start_s = max(t1, tick_i * self._time_step)
            end_s = min(t2, (tick_i + 1) * self._time_step - 1)
            n_s = end_s - start_s + 1
            rev_this_tick = rev_this_s * n_s
            
            rev += rev_this_tick
        return rev

    #=======================================================================
    #OCEAN minted & burned per month, as a count (#) and as USD ($)
    def OCEANmintedPrevMonth(self) -> float:
        return self._OCEANchangePrevMonth(self._total_OCEAN_minted__per_tick)
           
    def OCEANburnedPrevMonth(self) -> float:
        return self._OCEANchangePrevMonth(self._total_OCEAN_burned__per_tick)
    
    def OCEANmintedInUSDPrevMonth(self) -> float:
        return self._OCEANchangePrevMonth(self._total_OCEAN_minted_USD__per_tick)
    
    def OCEANburnedInUSDPrevMonth(self) -> float:
        return self._OCEANchangePrevMonth(self._total_OCEAN_burned_USD__per_tick)

    def _OCEANchangePrevMonth(self, O_per_tick) -> float:
        ticks_total = len(O_per_tick)

        if ticks_total == 0:
            return 0.0
        
        ticks_1mo = self._ticksOneMonth()
        if ticks_total <= ticks_1mo:
            return O_per_tick[-1]
        
        return O_per_tick[-1] - O_per_tick[-(ticks_1mo+1)]

    def _ticksOneMonth(self) -> int:
        """Number of ticks in one month"""
        ticks: int = math.ceil(S_PER_MONTH / float(self._time_step))
        return ticks


@enforce_types
def netlist_createLogData(state):
    """pass this to SimEngine.__init__() as argument `netlist_createLogData`"""
    F = False
    ss = state.ss
    kpis = state.kpis

    s = [] #for console logging
    dataheader = [] # for csv logging: list of string
    datarow = [] #for csv logging: list of float

    #SimEngine already logs: Tick, Second, Min, Hour, Day, Month, Year
    #So we log other things...

    am = state.getAgent("marketplaces1")
    #s += ["; # mkts=%s" % prettyBigNum(am._n_marketplaces,F)]
    dataheader += ["Num_mkts"]
    datarow += [am._n_marketplaces]

    onemkt_rev_mo = kpis.onemktMonthlyRevenueNow()
    onemkt_rev_yr = kpis.onemktAnnualRevenueNow()
    #s += ["; 1mkt_rev/mo=$%s,/yr=$%s" %
    #      (prettyBigNum(onemkt_rev_mo,F), prettyBigNum(onemkt_rev_yr,F))]
    dataheader += ["onemkt_rev/mo", "onemkt_rev/yr"]
    datarow += [onemkt_rev_mo, onemkt_rev_yr]

    allmkts_rev_mo = kpis.allmktsMonthlyRevenueNow()
    allmkts_rev_yr = kpis.allmktsAnnualRevenueNow()
    #s += ["; allmkts_rev/mo=$%s,/yr=$%s" %
    #      (prettyBigNum(allmkts_rev_mo,F), prettyBigNum(allmkts_rev_yr,F))]
    dataheader += ["allmkts_rev/mo", "allmkts_rev/yr"]
    datarow += [allmkts_rev_mo, allmkts_rev_yr]        

    ocean_rev_mo = kpis.oceanMonthlyRevenueNow()
    ocean_rev_yr = kpis.oceanAnnualRevenueNow()
    #s += ["; ocean_rev/mo=$%sm,/yr=$%s" %
    #      (prettyBigNum(ocean_rev_mo,F), prettyBigNum(ocean_rev_yr,F))]
    s += ["; ocean_rev/mo=$%sm" % prettyBigNum(ocean_rev_mo,F)]
    dataheader += ["ocean_rev/mo", "ocean_rev/yr"]
    datarow += [ocean_rev_mo, ocean_rev_yr]

    dataheader += ["ocean_rev_growth/mo", "ocean_rev_growth/yr"]
    datarow += [kpis.oceanMonthlyRevenueGrowth(),
                kpis.oceanAnnualRevenueGrowth()]

    ps30_valuation = kpis.valuationPS(30.0)
    dataheader += ["ps30_valuation"]
    datarow += [ps30_valuation]

    ov = state.overallValuation()
    dataheader += ["overall_valuation", "fundamentals_valuation",
                   "speculation_valuation"]
    s += ["; valn=$%s" % prettyBigNum(ov,F)]
    datarow += [ov, state.fundamentalsValuation(),
                state.speculationValuation()]

    tot_O_supply = state.OCEANsupply()
    s += ["; #OCEAN=%s" % prettyBigNum(tot_O_supply)]
    dataheader += ["tot_OCEAN_supply","tot_OCEAN_minted","tot_OCEAN_burned"]
    datarow += [tot_O_supply,
                state.totalOCEANminted(),
                state.totalOCEANburned()]

    dataheader += ["OCEAN_minted/mo","OCEAN_burned/mo"]
    datarow += [kpis.OCEANmintedPrevMonth(),
                kpis.OCEANburnedPrevMonth()]

    dataheader += ["OCEAN_minted_USD/mo","OCEAN_burned_USD/mo"]
    datarow += [kpis.OCEANmintedInUSDPrevMonth(),
                kpis.OCEANburnedInUSDPrevMonth()]

    O_price = state.OCEANprice()
    if O_price <= 10.0:
        s += ["; $OCEAN=$%.3f" % O_price]
    else:
        s += ["; $OCEAN=$%s" % prettyBigNum(O_price,F)]
    dataheader += ["OCEAN_price"]
    datarow += [O_price]

    gt_rev = kpis.grantTakersMonthlyRevenueNow()
    #s += ["; r&d/mo=$%s" % prettyBigNum(gt_rev,F)]
    dataheader += ["RND/mo"]
    datarow += [gt_rev]

    ratio = kpis.mktsRNDToSalesRatio()
    growth = ss.annualMktsGrowthRate(ratio)
    #s += ["; r&d/sales ratio=%.2f, growth(ratio)=%.3f" % (ratio, growth)]
    dataheader += ["rnd_to_sales_ratio", "mkts_annual_growth_rate"]
    datarow += [ratio, growth]

    dao = state.getAgent("ocean_dao") #RouterAgent
    dao_USD = dao.monthlyUSDreceived(state)
    dao_OCEAN = dao.monthlyOCEANreceived(state)
    dao_OCEAN_in_USD = dao_OCEAN * O_price
    dao_total_in_USD = dao_USD + dao_OCEAN_in_USD
    #s += ["; dao:[$%s/mo,%s OCEAN/mo ($%s),total=$%s/mo]" %
    #      (prettyBigNum(dao_USD,F), prettyBigNum(dao_OCEAN,F),
    #       prettyBigNum(dao_OCEAN_in_USD,F), prettyBigNum(dao_total_in_USD,F))]
    dataheader += ["dao_USD/mo", "dao_OCEAN/mo", "dao_OCEAN_in_USD/mo",
                   "dao_total_in_USD/mo"]
    datarow += [dao_USD, dao_OCEAN, dao_OCEAN_in_USD, dao_total_in_USD]

    #done
    return s, dataheader, datarow

@enforce_types
def netlist_plotInstructions(header: List[str], values):
    """
    Describe how to plot the information.
    tsp.do_plot() calls this

    :param: header: List[str] holding 'Tick', 'Second', ...
    :param: values: 2d array of float [tick_i, valuetype_i]
    :return: x: List[float] -- x-axis info on how to plot
    :return: y_params: List[YParam] -- y-axis info on how to plot
    """
    from util.plotutil import YParam, arrayToFloatList, \
        LINEAR, LOG, BOTH, \
        MULT1, MULT100, DIV1M, DIV1B, \
        COUNT, DOLLAR, PERCENT
    
    x = arrayToFloatList(values[:,header.index("Day")])
    
    y_params = [
        YParam(["OCEAN_price"], [""], "OCEAN Price", LOG, MULT1, DOLLAR),
        #YParam(["ocean_rev_growth/yr"], [""], "Annual Ocean Revenue Growth", BOTH, MULT100, PERCENT),
        YParam(["overall_valuation", "fundamentals_valuation","speculation_valuation"],
              ["Overall", "Fundamentals (P/S=30)", "Speculation"], "Valuation", LOG, DIV1M, DOLLAR),
        YParam(["dao_USD/mo", "dao_OCEAN_in_USD/mo", "dao_total_in_USD/mo"],
              ["Income as USD (ie network revenue)", "Income as OCEAN (ie from 51%; priced in USD)", "Total Income"],
              "Monthly OceanDAO Income", LOG, DIV1M, DOLLAR),
        YParam(["ocean_rev/yr","allmkts_rev/yr"], ["Ocean", "All marketplaces"],
              "Annual Revenue", LOG, DIV1M, DOLLAR),
        YParam(["tot_OCEAN_supply", "tot_OCEAN_minted", "tot_OCEAN_burned"],
              ["Total supply","Tot # Minted","Tot # Burned"], "OCEAN Token Count", BOTH, DIV1M, COUNT),
        YParam(["OCEAN_minted/mo", "OCEAN_burned/mo"], ["# Minted/mo", "# Burned/mo"],
              "Monthly # OCEAN Minted & Burned", BOTH, DIV1M, COUNT),
        YParam(["rnd_to_sales_ratio", "mkts_annual_growth_rate"], ["R&D/sales ratio", "Marketplaces annual growth rate"],
              "R&D/Sales Ratio and Marketplaces Growth Rate", BOTH, MULT100, PERCENT),
        YParam(["RND/mo"], [""], "Monthly R&D Spend", BOTH, DIV1M, DOLLAR),
        
        # YParam(["OCEAN_burned_USD/mo", "OCEAN_minted_USD/mo"],
        #       ["$ of OCEAN Burned/mo", "$ of OCEAN Minted/mo"],
        #       "Monthly OCEAN (in USD) Minted & Burned", LOG, DIV1M, DOLLAR),
        # YParam(["OCEAN_burned_USD/mo", "ocean_rev/mo", "allmkts_rev/mo"],
        #       ["$ OCEAN Burned monthly", "Ocean monthly revenue", "Marketplaces monthly revenue"],
        #       "Monthly OCEAN Burned & Revenues", LOG, DIV1M, DOLLAR),
    ]

    return (x, y_params)
