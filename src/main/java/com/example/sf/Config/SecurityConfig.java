package com.example.sf.Config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.annotation.web.configurers.HeadersConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
@RequiredArgsConstructor
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // private final CustomUserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests((requests) -> requests
                        .requestMatchers("/login", "/register", "/resources/","/main").permitAll() //이 페이지는 로그인 안해도 뜸
                        .anyRequest().authenticated()
                )
                .formLogin((form) -> form
                        .loginPage("/login") //로그인 페이지의 위치
                        .defaultSuccessUrl("/main", true) //로그인 성공시 도착할 페이지
                        .usernameParameter("userId")
                        .passwordParameter("password")
                        .permitAll()
                )
                .logout((logout) -> logout
                        .logoutUrl("/logout") //이곳으로 이동시 로그아웃
                        .logoutSuccessUrl("/login?logout") // 로그아웃 후 리디렉션될 페이지 설정
                        .permitAll()
                )
                .csrf(AbstractHttpConfigurer::disable)
                .headers(headers -> headers
                        .frameOptions(HeadersConfigurer.FrameOptionsConfig::disable) // 프레임 옵션 비활성화
                );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}