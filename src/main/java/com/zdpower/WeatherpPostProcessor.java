package com.zdpower;

import com.zdpower.repository.WeatherZDRespository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * @Auther: wll
 * @Date: 20-2-26 14:30
 * @Description:
 */
@Component
public class WeatherpPostProcessor {
    @Autowired
    private WeatherZDRespository weatherZDRespository;

    String cityname = "平湖";

    public void process(List<String> urls) {
        for (String url : urls) {
//            String result = HttpUtil.sendGet(url);
//            System.out.println(result);
//            Map<String, Object> resultMap = JSON.parseObject(result);
//            Map<String, String> weatherInfo = (Map<String, String>) resultMap.get("result");
//            WeatherZD weatherZD = new WeatherZD();
//
//            weatherZDRespository.save(weatherZD);
//            System.out.println(weatherInfo.get("humidity"));
        }
    }


    public void main(String[] args) throws ParseException {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        Date start = dateFormat.parse("2021-01-01");
        Date end = dateFormat.parse("2021-01-01");
        List<Date> dateList = getBetweenDates(start, end);
        List<String> urls = new ArrayList<>();
        for (Date date : dateList) {
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            urls.add("https://api.binstd.com/weather2/query?appkey=7a5708c07546e8d0&city=" + cityname + "&date=" + calendar.get(Calendar.YEAR) + "-" + (calendar.get(Calendar.MONTH) + 1)
                    + "-" + calendar.get(Calendar.DAY_OF_MONTH));
        }
        process(urls);
    }

    public static List<Date> getBetweenDates(Date start, Date end) {
        Set<Date> result = new HashSet<>();
        result.add(start);
        Calendar tempStart = Calendar.getInstance();
        tempStart.setTime(start);
        tempStart.add(Calendar.DAY_OF_YEAR, 1);

        Calendar tempEnd = Calendar.getInstance();
        tempEnd.setTime(end);
        while (tempStart.before(tempEnd)) {
            result.add(tempStart.getTime());
            tempStart.add(Calendar.DAY_OF_YEAR, 1);
        }
        result.add(end);
        List<Date> resultList = new ArrayList<>(result);
        Collections.sort(resultList);
        return resultList;
    }
}
