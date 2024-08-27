package com.example.sf.Repository;

import com.example.sf.Entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import javax.swing.text.html.parser.Entity;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<UserEntity, Long> {

    // 사용자 아이디(userId)로 사용자 검색
    Optional<UserEntity> findByUserId(String userId);

    @Query("SELECT u.userName FROM UserEntity u WHERE u.userId = :userid")
    String findUserNameByUserId(@Param("userid") String userid);

    // id로 유저 정보 가져오기
    @Query("SELECT u FROM UserEntity u WHERE u.userId = :userid")
    UserEntity findUserEntityByUserId(@Param("userid") String userid);

    // 사용자 이름으로 사용자 검색
    Optional<UserEntity> findByUserName(String userName); // 이 메서드를 추가

    // 이메일로 사용자 검색
    Optional<UserEntity> findByEmail(String email);

    // 전화번호로 사용자 검색
    Optional<UserEntity> findByPhone(String phone);

    @Query("SELECT u.id FROM UserEntity u WHERE u.userId = :userId")
    Long findUserNoByUserId(@Param("userId") String userId);
}