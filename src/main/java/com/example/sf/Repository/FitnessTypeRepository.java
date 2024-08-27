package com.example.sf.Repository;

import com.example.sf.Entity.FitnessTypeEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface FitnessTypeRepository extends JpaRepository<FitnessTypeEntity, Integer> {


    Optional<FitnessTypeEntity> findByName(String name);
    // name 컬럼만 가져오는 쿼리
    @Query("SELECT f.name FROM FitnessTypeEntity f")
    List<String> findAllFitnessTypeNames();

    Optional<FitnessTypeEntity> findByFitId(Long fitId);
}