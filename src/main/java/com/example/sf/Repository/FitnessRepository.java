package com.example.sf.Repository;

import com.example.sf.Entity.FitnessEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FitnessRepository extends JpaRepository<FitnessEntity, Integer> {
    // 추가적인 쿼리 메서드를 정의할 수 있습니다.
}
