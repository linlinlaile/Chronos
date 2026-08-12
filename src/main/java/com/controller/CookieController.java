package com.controller;

import com.entity.*;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.ModelAndView;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class CookieController {

    public static Map<String,StudyCookie> cookies = new HashMap<>();

    @GetMapping("/")
    public ModelAndView index() {
        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("index");
        modelAndView.addObject("cookies", cookies.values());
        return modelAndView;
    }

    @GetMapping("/drscan")
    public ModelAndView drscan() {
        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("drscan");
        List<User> users = new ArrayList<>();
        users.add(new User("333123","AAAAAAAAAA用户"));
        users.add(new User("21312412","BBBBBBBBBBBB用户"));
        modelAndView.addObject("users", users);
        return modelAndView;
    }

    @GetMapping("/getCookies")
    public ResultVO getCookies() {
        return ResultVO.success(cookies.values());
    }

    @PostMapping("/start")
    public ResultVO start(@RequestBody RequestDTO request) {
        Map<String,StudyCookie> cookiesTemp = new HashMap<>();
        if (request.getCookies() != null) {
            for (CookieDTO cookie : request.getCookies()) {
                if (!StringUtils.isEmpty(cookie.getName()) && !StringUtils.isEmpty(cookie.getValue())) {
                    if(cookies.containsKey(cookie.getName()) && cookies.get(cookie.getName()).getState().equals("正常")){
                        StudyCookie cookie1 = cookies.get(cookie.getName());
                        cookie1.setType(cookie.getType());
                        cookiesTemp.put(cookie.getName(),cookie1);
                        continue;
                    }
                    cookiesTemp.put(cookie.getName(),new StudyCookie(cookie.getName(), cookie.getValue(), cookie.getType()));
                }
            }
        }
        cookies = cookiesTemp;
        return ResultVO.success();
    }

    @PostMapping("/stop")
    public ResultVO sendCookies() {
        cookies.clear();
        return ResultVO.success();
    }
}