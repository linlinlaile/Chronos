package com.zdpower.repository;

import com.zdpower.entity.WeatherZD;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * @Auther: wll
 * @Date: 20-2-27 15:04
 * @Description:
 */
@Repository
public interface WeatherZDRespository extends JpaRepository<WeatherZD, Long> {
}
