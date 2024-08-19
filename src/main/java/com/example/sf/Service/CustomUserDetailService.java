package com.example.sf.Service;

import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import java.time.LocalDate;
import java.util.Collections;

import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

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

        updateLoginStreak(userEntity); // 연속 로그인 일수를 업데이트

        return new CustomUserDetails(
                userEntity.getUserId(),
                userEntity.getPassword(),
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER")),
                userEntity.getUserName(), // 추가 정보 전달
                userEntity.getConsecutiveLoginDays() // 연속 로그인 일수 전달
        );
    }

    private void updateLoginStreak(UserEntity userEntity) {
        LocalDate today = LocalDate.now();

        if (userEntity.getLastLoginDate() != null && userEntity.getLastLoginDate().equals(today.minusDays(1))) {
            userEntity.setConsecutiveLoginDays(userEntity.getConsecutiveLoginDays() + 1);
        } else if (userEntity.getLastLoginDate() == null || !userEntity.getLastLoginDate().equals(today)) {
            userEntity.setConsecutiveLoginDays(1);
        }

        userEntity.setLastLoginDate(today);
        userRepository.save(userEntity);
    }
}
