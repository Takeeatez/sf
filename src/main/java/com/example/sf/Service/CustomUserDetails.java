package com.example.sf.Service;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.User;

import java.util.Collection;

public class CustomUserDetails extends User {
    private final String userName;
    private int consecutiveLoginDays;

    public CustomUserDetails(String username, String password, Collection<? extends GrantedAuthority> authorities,
            String userName, int consecutiveLoginDays) {
        super(username, password, authorities);
        this.userName = userName; // 추가 데이터
        this.consecutiveLoginDays = consecutiveLoginDays; // 추가 데이터

    }

    public String getUserName() {
        return userName;
    }

    public int getConsecutiveLoginDays() {
        return consecutiveLoginDays;
    }
}