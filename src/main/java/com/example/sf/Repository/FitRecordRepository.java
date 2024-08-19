package com.example.sf.Repository;

import com.example.sf.Entity.FitRecordEntity;
import com.example.sf.Entity.UserEntity;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface FitRecordRepository extends JpaRepository<FitRecordEntity, Long> {

    Optional<FitRecordEntity> findTopByUserOrderByIdDesc(UserEntity user);

}
