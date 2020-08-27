SELECT WEEK(c2.report_date), c.city, sum(c2.confirmed), sum(c2.deaths) from cityinfo c 
join coviddata c2 on c.citycode = c2.citycode 
where c.city = 'Sacramento'
group by WEEK(c2.report_date), c.city 

