package com.hems.weather;

import com.common.SpringContextHolder;
import com.hems.weather.entity.WeatherData;
import com.hems.weather.entity.WeatherInfo;
import com.hems.weather.repository.WeatherDataRespository;
import com.hems.weather.repository.WeatherInfoRespository;
import lombok.extern.slf4j.Slf4j;
import us.codecraft.webmagic.ResultItems;
import us.codecraft.webmagic.Task;
import us.codecraft.webmagic.pipeline.Pipeline;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * @Auther: wll
 * @Date: 19-5-10 13:41
 * @Description:
 */

@Slf4j
public class WeatherPipeline implements Pipeline {
    private WeatherDataRespository weatherDataRespository = SpringContextHolder.getBean(WeatherDataRespository.class);
    private WeatherInfoRespository weatherInfoRespository = SpringContextHolder.getBean(WeatherInfoRespository.class);

    private static Set<String> holidays = new HashSet<>();
    private static Set<String> workdays = new HashSet<>();

    static {
        holidays.add("2019-1-1");
        holidays.add("2019-2-4");
        holidays.add("2019-2-5");
        holidays.add("2019-2-6");
        holidays.add("2019-2-7");
        holidays.add("2019-2-8");
        holidays.add("2019-2-9");
        holidays.add("2019-2-10");
        holidays.add("2019-4-5");
        holidays.add("2019-5-1");
        holidays.add("2019-5-2");
        holidays.add("2019-5-3");
        holidays.add("2019-5-4");
        holidays.add("2019-6-7");
        holidays.add("2019-9-13");
        holidays.add("2019-10-1");
        holidays.add("2019-10-2");
        holidays.add("2019-10-3");
        holidays.add("2019-10-4");
        holidays.add("2019-10-5");
        holidays.add("2019-10-6");
        holidays.add("2019-10-7");

        workdays.add("2019-2-2");
        workdays.add("2019-2-3");
        workdays.add("2019-4-28");
        workdays.add("2019-5-5");
        workdays.add("2019-9-29");
        workdays.add("2019-10-12");
    }

    @Override
    public void process(ResultItems resultItems, Task task) {
        String date = resultItems.get("date");
        String city = resultItems.get("city");
        List<WeatherInfo> weatherInfos = new ArrayList<>();
        Map<String, String[]> weatherTemp = resultItems.get("weathers");
        for (String time : weatherTemp.keySet()) {
            WeatherInfo w = new WeatherInfo();
            w.setDate(date);
            w.setTime(time);
            w.setCity(city);
            String[] weatherInfo = weatherTemp.get(time);
            String tempratureStr = weatherInfo[0].replaceAll("\\s*", "");
            ;
            String sky = weatherInfo[1].replaceAll("\\s*", "");
            w.setSky(sky);
            String desc = weatherInfo[2].replaceAll("\\s*", "");
            // 处理温度为int值
            int temperature = 0;
            if (tempratureStr.endsWith("°")) {
                temperature = Integer.parseInt(tempratureStr.substring(0, tempratureStr.length() - 1));
            } else {
                log.error("温度文字描述异常：" + tempratureStr);
                temperature = Integer.parseInt(tempratureStr);
            }
            w.setTemperature(temperature);
            // 处理湿度、体感温度、风向
            String[] descArr = desc.split("/");
            String humidityStr = descArr[0];
            int humidity = 0;
            if (humidityStr.startsWith("湿度") && humidityStr.endsWith("%")) {
                humidity = Integer.parseInt(humidityStr.substring(2, humidityStr.length() - 1));
            } else {
                log.error("湿度文字描述异常：" + humidityStr);
                humidity = Integer.parseInt(humidityStr);
            }
            w.setHumidity(humidity);
            String humTempStr = descArr[1];
            int humTemperature = 0;
            if (humTempStr.startsWith("体感") && humTempStr.endsWith("°")) {
                humTemperature = Integer.parseInt(humTempStr.substring(2, humTempStr.length() - 1));
            } else {
                log.error("体感温度文字描述异常：" + humTempStr);
                humTemperature = Integer.parseInt(humTempStr);
            }
            w.setHumTemperature(humTemperature);
            String wind = descArr[2];
            w.setWind(wind);
            w.setWbgt(calWbgt(temperature, humidity));
            weatherInfos.add(w);
            weatherInfoRespository.save(w);
        }
//        delAndSaveDataSource(weatherInfos);
    }

    /**
     * @Description: 按4小时平均处理后存储到数据库
     * @auther: wll
     * @date: 下午5:39 20-2-26
     * @param:
     * @return:
     */
    public void delAndSaveDataSource(List<WeatherInfo> weatherInfos) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-M-d");
        Collections.sort(weatherInfos);
        if (weatherInfos.size() != 24) {
            log.error(weatherInfos.get(0).getDate() + "天气信息不全");
            return;
        }
        // 判断是否是节假日
        boolean isHoliday = false;
        String dateStr = weatherInfos.get(0).getDate();
        if (holidays.contains(dateStr)) {
            isHoliday = true;
        } else if (workdays.contains(dateStr)) {
            isHoliday = false;
        } else {
            try {
                Date date = dateFormat.parse(dateStr);
                Calendar calendar = Calendar.getInstance();
                calendar.setTime(date);
                int dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK);
                if (dayOfWeek == Calendar.SATURDAY || dayOfWeek == Calendar.SUNDAY) {
                    isHoliday = true;
                }
            } catch (ParseException e) {
                e.printStackTrace();
            }
        }
        for (int i = 0; i < weatherInfos.size() / 4; i++) {
            WeatherData weatherData = new WeatherData();
            weatherData.setDate(dateStr);
            weatherData.setTimeScope(i);
            int temp = 0;
            int humidity = 0;
            int humTemp = 0;
            int wbgt = 0;
            for (int j = 0; j < 4; j++) {
                WeatherInfo weatherInfo = weatherInfos.get(i * 4 + j);
                temp += weatherInfo.getTemperature();
                humidity += weatherInfo.getHumidity();
                humTemp += weatherInfo.getHumTemperature();
                wbgt += weatherInfo.getWbgt();
            }
            weatherData.setTemprature(temp / 4);
            weatherData.setHumidity(humidity / 4);
            weatherData.setHumTemprature(humTemp / 4);
            weatherData.setWbgt(wbgt / 4);
            weatherData.setHoliday(isHoliday);
            weatherDataRespository.save(weatherData);
        }
    }

    /**
     * @Description: 计算湿球温度
     * @auther: wll
     * @date: 上午11:05 20-2-28
     * @param: [temperature, humidity]
     * @return: double
     */
    private double calWbgt(int temperature, int humidity) {
        return temperature * Math.atan(0.151977 * Math.sqrt(humidity + 8.313659)) + Math.atan(temperature + humidity)
                - Math.atan(humidity - 1.676331) + 0.00391838 * Math.pow(humidity, 1.5) * Math.atan(0.023101 * humidity) - 4.686035;
    }

}
