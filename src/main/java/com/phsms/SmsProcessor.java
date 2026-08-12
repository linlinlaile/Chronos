package com.phsms;

import com.alibaba.fastjson.JSON;
import com.wang.webmagic.KkpmhPipeline;
import com.wang.webmagic.PictureInfo;
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
public class SmsProcessor implements PageProcessor {
    // 1.抓取网站的相关配置，包括编码、抓取间隔、重试次数等
    private Site site = Site.me().setRetryTimes(3).setSleepTime(3000);

    //使用 selenium 来模拟用户的登录获取cookie信息
    public void login() {
        System.setProperty("webdriver.chrome.driver", "D:\\chromedriver.exe");
        WebDriver driver = new ChromeDriver();
        driver.get("http://smsapp.zj.sgcc.com.cn/ums-webapp/singleSignIn");
//        driver.get("http://www.baidu.com");
        driver.findElement(By.id("username")).clear();
        driver.findElement(By.id("username")).sendKeys("P00741452");
        driver.findElement(By.id("password")).clear();
        driver.findElement(By.id("password")).sendKeys("tk@741452");

        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        //模拟点击登录按钮
        driver.findElement(By.id("submi")).click();
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.findElement(By.className("el-select_input is-small")).sendKeys("18767101245");
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.findElement(By.className("el-select-dropdown_item hover")).click();
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.findElement(By.className("el-textarea_inner")).sendKeys("test1234516");
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.findElement(By.className("el-button el-button--primary el-button--small")).click();
        driver.close();
    }

    public void main(String[] args) {
        SmsProcessor processor = new SmsProcessor();
//        processor.login();
        Spider spider = Spider.create(processor)
                .addUrl("http://localhost:10573/ums-webapp.html")
                .thread(5);
        spider.run();
    }

    @Override
    public void process(Page page) {
        System.out.println("网页爬取成功:" + page.getUrl());
        String title = "";
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

    @Override
    public Site getSite() {
        return site.addHeader("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1");

    }
}
