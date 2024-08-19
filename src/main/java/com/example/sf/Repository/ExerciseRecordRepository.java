package com.example.sf.Repository;

import com.example.sf.Entity.ExerciseRecordEntity;
import com.example.sf.Entity.UserEntity;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface ExerciseRecordRepository extends JpaRepository<ExerciseRecordEntity, Long> {

    Optional<ExerciseRecordEntity> findTopByUserOrderByIdDesc(UserEntity user);

}
