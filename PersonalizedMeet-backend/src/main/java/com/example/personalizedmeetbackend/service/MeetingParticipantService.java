package com.example.personalizedmeetbackend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.example.personalizedmeetbackend.dto.MeetingParticipantRequest;
import com.example.personalizedmeetbackend.dto.MeetingParticipantResponse;
import com.example.personalizedmeetbackend.dto.MeetingParticipantRoleUpdateRequest;
import com.example.personalizedmeetbackend.dto.UserResponse;
import com.example.personalizedmeetbackend.exception.DuplicateMeetingParticipantException;
import com.example.personalizedmeetbackend.exception.MeetingNotFoundException;
import com.example.personalizedmeetbackend.exception.MeetingParticipantNotFoundException;
import com.example.personalizedmeetbackend.exception.UserNotFoundException;
import com.example.personalizedmeetbackend.model.Meeting;
import com.example.personalizedmeetbackend.model.MeetingParticipant;
import com.example.personalizedmeetbackend.model.User;
import com.example.personalizedmeetbackend.repository.MeetingParticipantRepository;
import com.example.personalizedmeetbackend.repository.MeetingRepository;
import com.example.personalizedmeetbackend.repository.UserRepository;

@Service
public class MeetingParticipantService {

    private final MeetingParticipantRepository meetingParticipantRepository;
    private final MeetingRepository meetingRepository;
    private final UserRepository userRepository;

    public MeetingParticipantService(
            MeetingParticipantRepository meetingParticipantRepository,
            MeetingRepository meetingRepository,
            UserRepository userRepository
    ) {
        this.meetingParticipantRepository = meetingParticipantRepository;
        this.meetingRepository = meetingRepository;
        this.userRepository = userRepository;
    }

    public MeetingParticipantResponse addParticipant(MeetingParticipantRequest request) {
        Meeting meeting = findMeetingOrThrow(request.getMeetingId());
        User user = findUserOrThrow(request.getUserId());

        if (meetingParticipantRepository.existsByMeetingIdAndUserId(meeting.getId(), user.getId())) {
            throw new DuplicateMeetingParticipantException(meeting.getId(), user.getId());
        }

        MeetingParticipant participant = new MeetingParticipant();
        participant.setMeeting(meeting);
        participant.setUser(user);
        participant.setParticipantRole(request.getParticipantRole());

        MeetingParticipant savedParticipant = meetingParticipantRepository.save(participant);
        return mapToResponse(savedParticipant);
    }

    public List<MeetingParticipantResponse> getParticipantsByMeeting(Long meetingId) {
        findMeetingOrThrow(meetingId);

        return meetingParticipantRepository.findByMeetingId(meetingId)
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    public MeetingParticipantResponse getParticipantById(Long id) {
        MeetingParticipant participant = findParticipantOrThrow(id);
        return mapToResponse(participant);
    }

    public MeetingParticipantResponse updateParticipantRole(
            Long id,
            MeetingParticipantRoleUpdateRequest request
    ) {
        MeetingParticipant participant = findParticipantOrThrow(id);
        participant.setParticipantRole(request.getParticipantRole());

        MeetingParticipant updatedParticipant = meetingParticipantRepository.save(participant);
        return mapToResponse(updatedParticipant);
    }

    public void removeParticipant(Long id) {
        MeetingParticipant participant = findParticipantOrThrow(id);
        meetingParticipantRepository.delete(participant);
    }

    private Meeting findMeetingOrThrow(Long id) {
        return meetingRepository.findById(id)
                .orElseThrow(() -> new MeetingNotFoundException(id));
    }

    private User findUserOrThrow(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
    }

    private MeetingParticipant findParticipantOrThrow(Long id) {
        return meetingParticipantRepository.findById(id)
                .orElseThrow(() -> new MeetingParticipantNotFoundException(id));
    }

    private MeetingParticipantResponse mapToResponse(MeetingParticipant participant) {
        User user = participant.getUser();
        UserResponse userResponse = new UserResponse(
                user.getId(),
                user.getName(),
                user.getEmail(),
                user.getRole(),
                user.getCreatedAt()
        );

        return new MeetingParticipantResponse(
                participant.getId(),
                participant.getMeeting().getId(),
                userResponse,
                participant.getParticipantRole(),
                participant.getJoinedAt()
        );
    }
}
