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
                        .requestMatchers("/login", "/register", "/resources/**", "/main", "/styles/**", "/scripts/**", "/images/**", "/test")
                        .permitAll() // 로그인 안 해도 접근 가능한 페이지
                        .anyRequest().authenticated()) // 그 외의 요청은 인증 필요
                .formLogin((form) -> form
                        .loginPage("/login") // 공통 로그인 페이지 경로 설정
                        .successHandler(new CustomAuthenticationSuccessHandler())
                        .usernameParameter("userId") // 사용자 아이디 파라미터 설정
                        .passwordParameter("password") // 패스워드 파라미터 설정
                        .permitAll())
                .logout((logout) -> logout
                        .logoutUrl("/logout") // 로그아웃 요청 경로
                        .logoutSuccessUrl("/login?logout") // 로그아웃 후 리디렉션 경로
                        .permitAll())
                .csrf(AbstractHttpConfigurer::disable) // CSRF 비활성화
                .headers(headers -> headers
                        .frameOptions(HeadersConfigurer.FrameOptionsConfig::disable) // 프레임 옵션 비활성화
                );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(); // 비밀번호 암호화를 위한 Encoder
    }
}
