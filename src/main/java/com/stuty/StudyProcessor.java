package com.stuty;

import com.hems.weather.WeatherPipeline;
import com.hems.weather.WeatherProcessor;
import com.wang.webmagic.PictureInfo;
import org.apache.commons.lang3.StringUtils;
import org.openqa.selenium.Cookie;
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
 * @Date: 19-5-10 13:40
 * @Description:
 */
@Component
public class StudyProcessor implements PageProcessor {
    public static Map<Integer, Integer> course = new HashMap<>();

    static {
        course.put(15, 16);
        course.put(16, 57);
        course.put(17, 489);
    }

    private static List<String> aa = new ArrayList<>();

    @Override
    public void process(Page page) {
        String url = page.getUrl().toString();
        System.out.println("网页爬取成功:" + url);
        List<Selectable> weatherInfo = page.getHtml().xpath("/html/body/div[@class='c-page']/div[@class='cont c']/div[@class='c-right-cont']/div[@class='all-course']/ul[@class='list c']/li[@class='item-box c']").nodes();
        for (Selectable htmlnode : weatherInfo) {
            HtmlNode node = (HtmlNode) htmlnode;
            String courseId = node.xpath("//li/div[@class=info]/p[@class=subject]/a/@href").toString().split("courseid=")[1];
            System.out.println(courseId);
            aa.add(courseId);
        }
    }

    @Override
    public Site getSite() {
        // 1.抓取网站的相关配置，包括编码、抓取间隔、重试次数等
        Site site = Site.me().setRetryTimes(3).setSleepTime(3000);
        site.addCookie("Cookie", "__sid__=6111608557; __loginuser__=339005199111170334; Hm_lvt_de1beef062ce941f1ebcd905eab09f70=1722309361,1722486664,1722828045,1723807270; BIGipServerxgx_web_pool=508236460.9028.0000; HZSRHANGZHOU=dc6dbdacee1f6c59d4bfb345ae236b8d; Stauthorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJrM2lzQCRkc281XiZBOEZIKkRGSSIsImF1ZCI6ImNsdyIsImlhdCI6MTczOTIzOTA5MiwibmJmIjoxNzM5MjM5MDkyLCJleHAiOjE3MzkyNDI2OTIsImRhdGEiOnsic3R1ZGVudGlkIjoiNDQ4MDE2In19.QK0dPda762Df5CHw_AgZtCkB3APbnaX0BQN6yoh-y0k");
        return site.addHeader("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1");
    }

    public void main(String[] args) throws ParseException {
        List<String> urls = new ArrayList<>();
        for (int i = 1; i <= 30; i++) {
            urls.add("https://learning.hzrs.hangzhou.gov.cn/course/index.php?offset=" + i + "&type=news&ckeywords=%E8%AF%B7%E8%BE%93%E5%85%A5%E5%85%B3%E9%94%AE%E5%AD%97%E6%9F%A5%E8%AF%A2&examtype=W&coursetype=15&");
        }

        StudyProcessor processor = new StudyProcessor();
        Spider spider = Spider.create(processor)
                .addUrl(urls.toArray(new String[]{}))
                .thread(5);
        spider.run();
        System.out.println(aa.size());
        String a = StringUtils.join(aa,",");
        System.out.println(a);
    }
}
