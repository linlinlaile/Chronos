package com.entity;

import lombok.Data;

/**
 * @Description: 视图层返回对象
 * @auther: wll
 * @date: 10:56 2018/6/14
 * @param:
 * @return:
 */
@Data
public class ResultVO<T> {

    /**
     * 错误码.
     */
    private Integer code;

    /**
     * 提示信息.
     */
    private String msg;

    /**
     * 具体内容.
     */
    private T data;

    public static <T> ResultVO<T> success(T t) {
        ResultVO resultVO = new ResultVO();
        resultVO.setData(t);
        resultVO.setCode(0);
        resultVO.setMsg("成功");
        return resultVO;
    }

    public static ResultVO success() {
        return success(null);
    }

    public static ResultVO error(String msg) {
        ResultVO resultVO = new ResultVO();
        resultVO.setCode(-1);
        resultVO.setMsg(msg);
        return resultVO;
    }

    public static ResultVO error(Integer code, String msg) {
        ResultVO resultVO = new ResultVO();
        resultVO.setCode(code);
        resultVO.setMsg(msg);
        return resultVO;
    }
}
