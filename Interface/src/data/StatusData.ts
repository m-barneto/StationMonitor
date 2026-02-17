export default interface LongDistanceSensor {
    zone: string;
    currentDistance: number;
    stableDistance: number;
    readingCount: number;
    reflectionStrength: number;
    temperature: number;
    occupiedDistance: number;
    isOccupied: string;
    duration: number;
}