package com.example.sf.Service;

import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;

import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Collections;

@Service
@Getter
@Setter
@RequiredArgsConstructor
@Transactional
public class CustomUserDetailService implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        UserEntity userEntity = userRepository.findByUserId(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        // UserEntity의 역할을 가져옵니다.
        String role = "ROLE_" + userEntity.getRole().name(); // ROLE_ADMIN 또는 ROLE_USER

        // Spring Security의 User 클래스를 사용하여 권한을 설정합니다.
        return new User(
                userEntity.getUserId(),
                userEntity.getPassword(),
                Collections.singletonList(new SimpleGrantedAuthority(role))
        );
    }
}