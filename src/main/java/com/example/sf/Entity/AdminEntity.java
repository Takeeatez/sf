package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Entity
@Table(name = "admin")
@Getter
@Setter
public class AdminEntity {

    @Id
    @Column(length = 255)
    private String id;

    @Column(length = 255)
    private String username;

    @Column(length = 255)
    private String password;

    @Column(length = 255)
    private String name;

    @OneToMany(mappedBy = "admin", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<FitnessTypeEntity> fitnessTypes;
}
