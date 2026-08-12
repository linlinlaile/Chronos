package com.entity;

import lombok.Data;

@Data
public class CookieDTO {
        private String name;
        private String value;
        private Integer type; // 类型改为 Integer
    }