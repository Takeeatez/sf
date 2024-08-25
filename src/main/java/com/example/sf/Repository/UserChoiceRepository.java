package com.example.sf.Repository;

import com.example.sf.Entity.UserChoiceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserChoiceRepository extends JpaRepository<UserChoiceEntity, String> {
    // 추가적인 쿼리가 필요한 경우 여기에 정의할 수 있습니다.
}
