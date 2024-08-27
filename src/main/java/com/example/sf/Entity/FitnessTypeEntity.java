package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@Entity
@Table(name = "FitnessType")
public class FitnessTypeEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long fitId;

    @Column(length = 20)
    private String name;

    @Column(length = 20)
    private String description;

    @OneToMany(mappedBy = "fitnessType", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<UserChoiceEntity> userChoices;

}