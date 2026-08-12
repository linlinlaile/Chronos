package com.hems.weather;

import org.springframework.stereotype.Component;
import us.codecraft.webmagic.Page;
import us.codecraft.webmagic.Site;
import us.codecraft.webmagic.Spider;
import us.codecraft.webmagic.processor.PageProcessor;
import us.codecraft.webmagic.scheduler.RedisScheduler;
import us.codecraft.webmagic.selector.HtmlNode;
import us.codecraft.webmagic.selector.Selectable;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * @Auther: wll
 * @Date: 20-2-26 14:30
 * @Description:
 */
public class WeatherProcessor implements PageProcessor {
    String cityname = "江宁";
    static String cityUrl = "liuhequ";
    @Override
    public void process(Page page) {
        String url = page.getUrl().toString();
        System.out.println("网页爬取成功:" + url);
        List<Selectable> weatherInfo = page.getHtml().xpath("//ul[@class=tqlist]").nodes().get(0).xpath("//li").nodes();
        Map<String, String[]> weatherTemp = new HashMap<>();
        for (Selectable htmlnode : weatherInfo) {
            HtmlNode node = (HtmlNode) htmlnode;
            String time = node.xpath("//span[@class=tqtit]/text()").toString();
            String temperature = node.xpath("//span[@class=tqwds]/text()").toString();
            String sky = node.xpath("//span[@class=tqpics]/img/@alt").toString();
            String desc = node.xpath("//span[@class=tqdesc]/text()").toString();
            weatherTemp.put(time, new String[]{temperature, sky, desc});
        }
        page.putField("weathers", weatherTemp);
        page.putField("city",cityname);
        page.putField("date", url.substring(url.lastIndexOf("/")+1,url.lastIndexOf(".")));
    }

    @Override
    public Site getSite() {
        // 1.抓取网站的相关配置，包括编码、抓取间隔、重试次数等
        Site site = Site.me().setRetryTimes(3).setSleepTime(3000);
        return site;
    }

    public static void main(String[] args) throws ParseException {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        Date start = dateFormat.parse("2018-08-25");
        Date end = dateFormat.parse("2018-08-25");
        List<Date> dateList = getBetweenDates(start, end);
        List<String> urls = new ArrayList<>();
        for (Date date : dateList) {
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            urls.add("https://mtianqi.911cha.com/"+cityUrl+"/" + calendar.get(Calendar.YEAR) + "-" + (calendar.get(Calendar.MONTH) + 1)
                    + "-" + calendar.get(Calendar.DAY_OF_MONTH) + ".html");
        }
        WeatherProcessor processor = new WeatherProcessor();
        Spider spider = Spider.create(processor)
                .addUrl(urls.toArray(new String[]{}))
                .addPipeline(new WeatherPipeline())
                //通过redisscheduler去重
                .setScheduler(new RedisScheduler("127.0.0.1"))
                .thread(5);
        spider.run();
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
