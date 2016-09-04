'''
    初始化函数, 必须实现
'''
def initialize(context):
    # 非复权价格, 消除前视偏差(未来信息)
    set_option('use_real_price', True)
    # 详见 https://www.joinquant.com/indexData
    g.stocks = get_index_stocks('399006.XSHE')
    # 持股数
    g.buy_count = 5


'''
    查询财务数据
        股票财务数据 详见 https://www.joinquant.com/data/dict/fundamentals

        返回一个 pandas.DataFrame, 每一行对应数据库返回的每一行
        (可能是几个表的联合查询结果的一行), 列索引是你查询的所有字段
        注意：
        1. 为了防止返回数据量过大, 我们每次最多返回10000行
        2. 当相关股票上市前、退市后，财务数据返回各字段为空
'''
def get_fund(a):
    q = query(
            valuation,
        ).filter(
            # 市值小于300亿, 市盈率介于0~30,
            valuation.pe_ratio < 30,
            valuation.market_cap < 300,
            valuation.pe_ratio > 0,
            # 这里不能使用 in 操作, 要使用in_()函数
            valuation.code.in_(a)
    ).order_by(
        # 按市盈率升序排列
            valuation.pe_ratio.asc()
    ).limit(
        # 最多返回80个
        80
    )
    df = get_fundamentals(q)
    return df


'''
    周期执行函数, 必须在initialize中调用.
'''
def handle_data(context, data):
    df = get_fund(g.stocks)
# TODO 实现策略
#    stocks = df.code.values
#    stocks = filter_paused_stock(stocks)
#    stocks = stocks[:g.buy_count]
#    for stock in context.portfolio.positions:
#        if stock not in stocks:
#            order_target_value(stock, 0)
#    if len(context.portfolio.positions) < g.buy_count:
#        buy_value = context.portfolio.portfolio_value / (g.buy_count - len(context.portfolio.positions))
#        for stock in stocks:
#            if stock not in context.portfolio.positions:
#                order_target_value(stock, buy_value)
#            if len(context.portfolio.positions) >= g.buy_count:
#                break


# 过滤停牌
def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]


# 过滤黑名单股票
def filter_blacklist_stock(context, stock_list):
    blacklist = get_blacklist()
    if context.run_params.type != 'sim_trade':
        blacklist = []
    return [stock for stock in stock_list if stock not in blacklist]

def get_blacklist():
    # 黑名单一览表，暂停上市风险 2016.9.4
    blacklist = ["600656.XSHG", "600421.XSHG", "600733.XSHG", "300399.XSHE"]
    return blacklist