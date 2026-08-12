package com.wang.webmagic;

import com.alibaba.fastjson.JSON;
import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.Select;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import redis.clients.jedis.Jedis;
import us.codecraft.webmagic.Page;
import us.codecraft.webmagic.Site;
import us.codecraft.webmagic.Spider;
import us.codecraft.webmagic.processor.PageProcessor;
import us.codecraft.webmagic.scheduler.RedisScheduler;
import us.codecraft.webmagic.selector.HtmlNode;
import us.codecraft.webmagic.selector.Selectable;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * @Auther: wll
 * @Date: 19-5-10 13:40
 * @Description:
 */
@Component
public class KkpmhProcessor implements PageProcessor {
    // 1.抓取网站的相关配置，包括编码、抓取间隔、重试次数等
    private Site site = Site.me().setRetryTimes(3).setSleepTime(3000);
    //            .setHttpProxy(new HttpHost("45.32.50.126",4399));

    public static final String INDEX_URL = "";

    public static final String URL_LIST = "";

    //用来存储cookie信息
    private Set<Cookie> cookies;

    public void setCookies(Set<Cookie> cookies) {
        this.cookies = cookies;
    }

    @Override
    public void process(Page page) {
        System.out.println("网页爬取成功:" + page.getUrl());
        String title = "";
        //列表页
        if (page.getUrl().regex(URL_LIST).match() || page.getUrl().get().equals(INDEX_URL) || page.getUrl().get().equals(INDEX_URL + "/")) {
            page.addTargetRequests(page.getHtml().xpath("//article//h2[@class=entry-title]").links().all());
            page.addTargetRequests(page.getHtml().xpath("//div[@class=nav-links]/[@class=next]").links().all());
        } else {
            title = page.getHtml().xpath("//article/footer/span[2]/a/text()").toString();
            page.putField("title", title);
            page.putField("chapters", page.getHtml().xpath("//h1[@class='entry-title']/text()").toString());

            List<Selectable> htmlnodes = page.getHtml().xpath("//div[@class='cartoon']/img").nodes();
            List<PictureInfo> pictureInfos = new ArrayList<>();
            for (Selectable htmlnode : htmlnodes) {
                HtmlNode node = (HtmlNode) htmlnode;
                String pictureName = node.xpath("/img/@alt").toString();
                String pictureUrl = node.xpath("/img/@data-lazy-src").toString();
                PictureInfo pictureInfo = new PictureInfo(pictureName, pictureUrl);
                pictureInfos.add(pictureInfo);
            }
            page.putField("pictures", pictureInfos);
        }
        if (StringUtils.isEmpty(title)) {
            page.setSkip(true);
        }
    }

    @Override
    public Site getSite() {
        //将获取到的cookie信息添加到webmagic中
        for (Cookie cookie : cookies) {
            site.addCookie(cookie.getName().toString(), cookie.getValue().toString());
        }

        return site.addHeader("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1");
    }

    //使用 selenium 来模拟用户的登录获取cookie信息
    public void login() {
        System.setProperty("webdriver.chrome.driver", "/home/telek/Other/ChromeDriver/chromedriver_linux64/chromedriver");
        WebDriver driver = new ChromeDriver();
        driver.get("https://kkpmh.com/login/");
//        driver.get("http://www.baidu.com");
        driver.findElement(By.id("username-10628")).clear();
        driver.findElement(By.id("username-10628")).sendKeys("435044190@qq.com");
        driver.findElement(By.id("user_password-10628")).clear();
        driver.findElement(By.id("user_password-10628")).sendKeys("dakweP-sakgur-6pemmi");
        Select sel = new Select(driver.findElement(By.id("user_password-10628")));
        sel.selectByIndex(0);

        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        //模拟点击登录按钮
        driver.findElement(By.id("um-submit-btn")).click();
        //获取cookie信息
        cookies = driver.manage().getCookies();
        //将cookie存入redis中
        Jedis jedis = new Jedis("106.15.226.131", 6379);
        jedis.set("cookies", JSON.toJSONString(cookies));
        driver.close();
    }

    public static void main(String[] args) {
        KkpmhProcessor processor = new KkpmhProcessor();
        Jedis jedis = new Jedis("106.15.226.131", 6379);
        if (!jedis.exists("cookies")) {
            //调用selenium，进行模拟登录
            processor.login();
        } else {
            String cookiesStr = jedis.get("cookies");
            List<Cookie> cookies = (List<Cookie>) JSON.parseArray(cookiesStr, Cookie.class);
            processor.setCookies(cookies.stream().collect(Collectors.toSet()));
        }
        Spider spider = Spider.create(processor)
                .addUrl(INDEX_URL)
                .addPipeline(new KkpmhPipeline())
                //通过redisscheduler去重
                .setScheduler(new RedisScheduler("106.15.226.131"))
                .thread(5);
        spider.run();
    }
}
