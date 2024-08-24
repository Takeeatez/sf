package com.example.sf.Repository;

import com.example.sf.Entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<UserEntity, Long> {

    // 사용자 아이디(userId)로 사용자 검색
    Optional<UserEntity> findByUserId(String userId);

    Optional<UserEntity> findByUserName(String userName); // 이 메서드를 추가

    // 이메일로 사용자 검색
    Optional<UserEntity> findByEmail(String email);

    // 전화번호로 사용자 검색
    Optional<UserEntity> findByPhone(String phone);
}
