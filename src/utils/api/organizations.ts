import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

export interface ClubOrganization {
  id: number;
  name: string;
  description: string;
}

export const getClubOrganizations = async (): Promise<ClubOrganization[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/organizations/get_club_orgs`, {
      withCredentials: true,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch club organizations:', error);
    throw error;
  }
};

export const addOrgToSchedule = async (scheduleId: number, orgId: number): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/users/add_org_to_schedule`, {
      schedule_id: scheduleId,
      org_id: orgId,
    }, {
      withCredentials: true,
    });
  } catch (error) {
    console.error('Failed to add organization to schedule:', error);
    throw error;
  }
};

export const removeOrgFromSchedule = async (scheduleId: number, orgId: number): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/users/remove_org_from_schedule`, {
      schedule_id: scheduleId,
      org_id: orgId,
    }, {
      withCredentials: true,
    });
  } catch (error) {
    console.error('Failed to remove organization from schedule:', error);
    throw error;
  }
};
