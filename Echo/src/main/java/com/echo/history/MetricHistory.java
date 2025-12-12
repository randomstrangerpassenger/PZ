package com.echo.history;

import java.util.Arrays;

/**
 * 메트릭 시계열 데이터 저장소 (Ring Buffer)
 */
public class MetricHistory {
    private final double[] buffer;
    private int head = 0;
    private int size = 0;
    private final int capacity;
    private final String name;

    public MetricHistory(String name, int capacity) {
        this.name = name;
        this.capacity = capacity;
        this.buffer = new double[capacity];
    }

    public synchronized void add(double value) {
        buffer[head] = value;
        head = (head + 1) % capacity;
        if (size < capacity) {
            size++;
        }
    }

    public synchronized double[] toArray() {
        if (size < capacity) {
            return Arrays.copyOf(buffer, size);
        }

        double[] result = new double[capacity];
        // head is the index of the *next* write, so the oldest element is at head (if
        // full)
        // We want chronological order: oldest -> newest

        int current = head; // oldest element
        for (int i = 0; i < capacity; i++) {
            result[i] = buffer[current];
            current = (current + 1) % capacity;
        }
        return result;
    }

    public String getName() {
        return name;
    }

    public int getSize() {
        return size;
    }

    public int getCapacity() {
        return capacity;
    }
}
