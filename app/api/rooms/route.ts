import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const householdId = searchParams.get('household_id');

    if (!householdId) {
      return NextResponse.json({ error: 'Household ID is required' }, { status: 400 });
    }

    // For now, we'll use localStorage data since we don't have a real backend
    // In a real application, this would fetch from a database
    
    // Return mock data for testing
    const mockRooms = [
      { id: '1', name: 'Living Room', type: 'living_room' },
      { id: '2', name: 'Kitchen', type: 'kitchen' },
      { id: '3', name: 'Bedroom', type: 'bedroom' },
      { id: '4', name: 'Bathroom', type: 'bathroom' }
    ];

    return NextResponse.json(mockRooms);
  } catch (error) {
    console.error('Error in rooms API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 