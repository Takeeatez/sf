package com.example.sf.Service;

import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;

import org.springframework.security.core.authority.SimpleGrantedAuthority;
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

        // Role 타입을 String으로 변환하여 SimpleGrantedAuthority 생성자에 전달
        String role = userEntity.getRole().name(); // Role enum의 이름을 String으로 변환
        SimpleGrantedAuthority authority = new SimpleGrantedAuthority("ROLE_" + role);

        return new CustomUserDetails(
                userEntity.getUserId(),
                userEntity.getPassword(),
                Collections.singletonList(authority),
                userEntity.getUserName() // 추가 정보 전달
        );
    }
}
