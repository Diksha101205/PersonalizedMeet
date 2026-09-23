package com.example.personalizedmeetbackend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.example.personalizedmeetbackend.dto.MeetingRequest;
import com.example.personalizedmeetbackend.dto.MeetingResponse;
import com.example.personalizedmeetbackend.dto.UserResponse;
import com.example.personalizedmeetbackend.exception.DuplicateMeetingCodeException;
import com.example.personalizedmeetbackend.exception.MeetingNotFoundException;
import com.example.personalizedmeetbackend.exception.UserNotFoundException;
import com.example.personalizedmeetbackend.model.Meeting;
import com.example.personalizedmeetbackend.model.MeetingStatus;
import com.example.personalizedmeetbackend.model.User;
import com.example.personalizedmeetbackend.repository.MeetingRepository;
import com.example.personalizedmeetbackend.repository.UserRepository;

@Service
public class MeetingService {

    private final MeetingRepository meetingRepository;
    private final UserRepository userRepository;

    public MeetingService(MeetingRepository meetingRepository, UserRepository userRepository) {
        this.meetingRepository = meetingRepository;
        this.userRepository = userRepository;
    }

    public MeetingResponse createMeeting(MeetingRequest request) {
        User creator = findUserOrThrow(request.getCreatedById());
        String meetingCode = generateUniqueMeetingCode();

        Meeting meeting = new Meeting();
        meeting.setTitle(request.getTitle());
        meeting.setDescription(request.getDescription());
        meeting.setMeetingCode(meetingCode);
        meeting.setCreatedBy(creator);
        meeting.setStatus(MeetingStatus.SCHEDULED);

        Meeting savedMeeting = meetingRepository.save(meeting);
        return mapToResponse(savedMeeting);
    }

    public MeetingResponse getMeetingById(Long id) {
        Meeting meeting = findMeetingOrThrow(id);
        return mapToResponse(meeting);
    }

    public List<MeetingResponse> getAllMeetings() {
        return meetingRepository.findAll()
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    public MeetingResponse updateMeeting(Long id, MeetingRequest request) {
        Meeting meeting = findMeetingOrThrow(id);
        User creator = findUserOrThrow(request.getCreatedById());

        meeting.setTitle(request.getTitle());
        meeting.setDescription(request.getDescription());
        meeting.setCreatedBy(creator);

        if (request.getStatus() != null) {
            meeting.setStatus(request.getStatus());
        }

        Meeting updatedMeeting = meetingRepository.save(meeting);
        return mapToResponse(updatedMeeting);
    }

    public void deleteMeeting(Long id) {
        Meeting meeting = findMeetingOrThrow(id);
        meetingRepository.delete(meeting);
    }

    private Meeting findMeetingOrThrow(Long id) {
        return meetingRepository.findById(id)
                .orElseThrow(() -> new MeetingNotFoundException(id));
    }

    private User findUserOrThrow(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
    }

    private String generateUniqueMeetingCode() {
        long nextNumber = meetingRepository.count() + 1;
        String meetingCode = formatMeetingCode(nextNumber);

        int attempts = 0;
        while (meetingRepository.existsByMeetingCode(meetingCode)) {
            attempts++;
            nextNumber++;
            meetingCode = formatMeetingCode(nextNumber);

            if (attempts > 1000) {
                throw new DuplicateMeetingCodeException(meetingCode);
            }
        }

        return meetingCode;
    }

    private String formatMeetingCode(long number) {
        return String.format("PMP-%03d", number);
    }

    private MeetingResponse mapToResponse(Meeting meeting) {
        User creator = meeting.getCreatedBy();

        UserResponse creatorResponse = new UserResponse(
                creator.getId(),
                creator.getName(),
                creator.getEmail(),
                creator.getRole(),
                creator.getCreatedAt()
        );

        return new MeetingResponse(
                meeting.getId(),
                meeting.getTitle(),
                meeting.getDescription(),
                meeting.getMeetingCode(),
                creatorResponse,
                meeting.getCreatedAt(),
                meeting.getStatus()
        );
    }
}
