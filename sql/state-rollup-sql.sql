SELECT province 'state', sum(c2.active_cases) 'active cases', sum(c2.deaths) 'deaths' 
FROM covid.cityinfo c
Join coviddata c2 on c.citycode = c2.citycode 
where c.province = 'California' and c2.report_date = (SELECT max(c3.report_date) from coviddata c3 )
group by c.province 

