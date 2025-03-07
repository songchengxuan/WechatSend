import configparser


def sqlDefine():
    # 第一张表——连锁区域销售表
    ret_sql_1 = '''
        select
            branch_name 
            ,org_department_name 
            ,operational_region_desc 
            ,business_manager_name
            ,billon_source
            ,sum(business_amount) business_amount 
            ,sum(tag_price) tag_price 
        from ads.ads_fact_salesforecast_store_daytime
        where sdate = current_date
        group by branch_name 
            ,org_department_name 
            ,operational_region_desc 
            ,business_manager_name
            ,billon_source
        order by branch_name, org_department_name
        '''

    # 第二张表——TOP50和BOTTOM50门店销售
    ret_sql_2 = '''
    with tx as (
    select 
        row_number() over(order by business_amount desc) num_desc
        ,row_number() over(order by business_amount asc) num_asc
        ,t.*
    from 
        (select
            branch_name 
            ,store_id
            ,store_name 
            ,sum(business_amount) business_amount
        from ads.ads_fact_salesforecast_store_daytime
        where sdate = current_date
        and business_amount is not null
        and substring(store_name,1,2) not in ('连锁','红豆','销售','运营') 
        group by branch_name ,store_id,store_name 
        ) t
    )
    select 
        num_desc
        ,null as num_asc
        ,branch_name 
        ,store_name
        ,store_id
        ,business_amount 
    from tx where num_desc <= 50
    union all
    select 
        null as num_desc
        ,num_asc
        ,branch_name 
        ,store_name
        ,store_id
        ,business_amount 
    from tx where num_asc <= 50
    order by num_desc asc,num_asc asc
    '''
    # 第三张表——部门主推销售
    ret_sql_3 = '''
    select 
        coalesce(t1.branch_name,t2.branch_name) branch_name
        ,coalesce(t1.org_department_name,t2.org_department_name) org_department_name
        ,coalesce(t1.main_attribute,t2.main_attribute) main_attribute
        ,coalesce(t1.business_qty_today,0) business_qty_today
        ,coalesce(t2.acc_business_qty,0) acc_business_qty
    from 
        (select 
            branch_name 
            ,org_department_name 
            ,main_attribute 
            ,sum(business_qty) business_qty_today
        from ads.ads_fact_sales_store_skc_daytime
        where sdate = current_date
        and main_attribute is not null
        and org_department_name <> '厂部'
        and year_season_combine = '2022秋冬'
        group by branch_name, org_department_name, main_attribute 
        ) t1
    left join 
        (select 
            branch_name 
            ,org_department_name 
            ,main_attribute 
            ,sum(acc_business_qty) acc_business_qty
        from ads.ads_sales_inout_store_skc_day_product_yesterday
        where main_attribute is not null
        and org_department_name <> '厂部'
        and year_season_combine = '2022秋冬'
        group by branch_name, org_department_name, main_attribute 
        ) t2
    on t1.branch_name = t2.branch_name
    and t1.org_department_name = t2.org_department_name
    and t1.main_attribute = t2.main_attribute
    '''
    # 第四张表——季节品类前七
    ret_sql_4 = '''
    select 
        *
    from 
        (select
            row_number() over(partition by classification_zhonglei_desc order by business_qty desc) num_desc
            ,classification_zhonglei_desc 
            ,skc
            ,business_qty 
            ,business_amount
            ,round(business_amount/case when (sum(business_amount) over (partition by classification_zhonglei_desc))=0 then null else sum(business_amount) over (partition by classification_zhonglei_desc) end, 4) business_amount_percentage
        from 
            (select 
                classification_zhonglei_desc 
                ,skc 
                ,sum(business_qty) business_qty
                ,sum(business_amount) business_amount
            from ads.ads_fact_sales_store_skc_daytime
            where sdate = current_date 
            and classification_dalei_desc not in ('其它','饰品')
            and classification_zhonglei_desc is not null 
            and business_amount <> 0
            group by classification_zhonglei_desc, skc
            ) td
        ) tx
    where tx.num_desc <= 7
        '''
    # 第五张表——门店主推销售
    ret_sql_5 = '''
        with tx as
        (select 
            row_number() over(partition by classification_dalei_desc order by business_amount desc) rank_desc
            ,row_number() over(partition by classification_dalei_desc order by business_amount asc) rank_asc
            ,*
        from 
            (select
                classification_dalei_desc 
                ,branch_name 
                ,store_name
                ,sum(business_amount) business_amount
                ,sum(business_qty) business_qty
            from ads.ads_fact_sales_store_skc_daytime
            where sdate = current_date
            and substring(store_name,1,2) not in ('连锁','红豆','销售','运营') 
            and classification_dalei_desc not in ('其它','饰品')
            and classification_zhonglei_desc is not null 
            group by classification_dalei_desc ,branch_name ,store_name
            ) td
        )
        select 
            rank_desc
            ,null as rank_asc
            ,classification_dalei_desc 
            ,branch_name 
            ,store_name
            ,business_amount
            ,business_qty
        from tx 
        where tx.rank_desc <= 50
        union
        select 
            null as rank_desc
            ,rank_asc
            ,classification_dalei_desc 
            ,branch_name 
            ,store_name
            ,business_amount
            ,business_qty
        from tx 
        where tx.rank_asc <= 50
    '''
    # 第六张表——小时时段销售
    ret_sql_6 = '''
        select 
            sdate,hours,business_amount
        from
            (select 
                sdate
                ,hours
                ,sum(business_amount) business_amount
            from
                (select
                    pay_date::date sdate
                    ,date_part('hours', pay_date) hours
                    ,business_amount 
                from dw.dwd_fact_online_ordergoods
                where pay_date::date = current_date - interval '1 year'
                union all
                select
                    pay_date::date sdate
                    ,date_part('hours', pay_date) hours
                    ,business_amount 
                from dw.dwd_fact_offline_ordergoods
                where pay_date::date = current_date - interval '1 year'
                ) td
            group by sdate,hours
            ) tx1
        union all
        select sdate,hours,business_amount
        from
            (select 
                sdate
                ,hours
                ,sum(business_amount) business_amount
            from
                (select 
                    to_timestamp(rq)::date sdate
                    ,date_part('hours', to_timestamp(rq)) hours
                    ,je business_amount
                from ods.ods_ipos_qtlsd_daytime
                where to_timestamp(rq) >= current_date - interval '1 days'
                and to_timestamp(rq) < date_trunc('hours',current_timestamp)
                and zddm not like  '%*_%' escape '*'
                and upper(djbh) not like '%GD%'
                union all 
                select 
                    ordertime::date sdate
                    ,date_part('hours',ordertime) hours
                    ,payamount business_amount
                from ods.ods_mall_sales_order_daytime
                where ordertime >= current_date - interval '1 days'
                and ordertime < date_trunc('hours',current_timestamp)
                and orderstatus in('16','4','8','2')
                ) td
            group by sdate,hours
            ) tx2
        order by sdate desc, hours asc
    '''
    ret_sql_7 = '''
    select 
        coalesce(t1.org_department_name,t2.org_department_name) org_department_name
        ,coalesce(t1.org_org_department_id,t2.org_org_department_id) org_org_department_id
        ,coalesce(t1.satnr,t2.satnr) satnr
        ,coalesce(t1.business_qty,0) business_qty
        ,coalesce(t2.business_qty,0) acc_business_qty
    from 
        (select 
            org_department_name 
            ,org_org_department_id 
            ,satnr 
            ,sum(business_qty) business_qty
        from ads.ads_fact_sales_store_skc_daytime 
        where satnr in ('HM1C008KTH1','HM3C008KTH1','HM1C188LPH1',
        'HM3C188LPH1','HM1C008LPH1','HM3C008LPH1','HM3C008LQH1',
        'HM1C008LQH1','HM2C012KTH1','HM2C011KTH1','HM6C008KTH1',
        'HM6C009KTH1','HM6C001KTH1','HM6K008GNH1','HM6K008FAH1')
        and sdate = current_date
        group by org_department_name,org_org_department_id,satnr
        ) t1
    full join 
        (select 
            org_department_name 
            ,org_org_department_id 
            ,satnr 
            ,sum(business_qty) business_qty
        from ads.ads_sales_source_store_skc_day 
        where satnr in ('HM1C008KTH1','HM3C008KTH1','HM1C188LPH1',
        'HM3C188LPH1','HM1C008LPH1','HM3C008LPH1','HM3C008LQH1',
        'HM1C008LQH1','HM2C012KTH1','HM2C011KTH1','HM6C008KTH1',
        'HM6C009KTH1','HM6C001KTH1','HM6K008GNH1','HM6K008FAH1')
        and sdate >= '2022-08-19'
        group by org_department_name,org_org_department_id,satnr
        ) t2
    on t1.org_org_department_id = t2.org_org_department_id
    and t1.satnr = t2.satnr
    order by t1.satnr asc, t1.org_org_department_id asc
    '''
    ret_sql_8 = '''
    select 
        sdate 
        ,branch_name
        ,org_org_department_id 
        ,org_department_name
        ,operational_region_desc 
        ,sum(business_amount) business_amount
        ,sum(business_qty) business_qty
        ,sum(nums_of_effective) nums_of_effective
    from ads.ads_fact_salesforecast_store_daytime
    where sdate = current_date
    group by sdate,branch_name,org_org_department_id,org_department_name
    ,operational_region_desc
    union all
    select 
        sdate 
        ,branch_name
        ,'累计' as org_org_department_id
        ,'累计' as org_department_name 
        ,'累计' as operational_region_desc 
        ,sum(business_amount) business_amount
        ,sum(business_qty) business_qty
        ,sum(nums_of_effective) nums_of_effective
    from ads.ads_fact_salesforecast_store_day 
    where sdate = current_date - 364
    group by sdate,branch_name
    order by sdate 
    '''
    return ret_sql_1, ret_sql_2, ret_sql_3, ret_sql_4, ret_sql_5, ret_sql_6, ret_sql_7, ret_sql_8


