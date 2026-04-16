#include <windows.h>
#include <iostream>

struct SharedData {
    float x;
    float y;
    float vel_x;
    float vel_y;
    float acc_x;
    float acc_y;
};

int main() {

    HANDLE hMap = OpenFileMapping(FILE_MAP_ALL_ACCESS, FALSE, L"MySharedMemory");

    if (!hMap) {
        std::cout << "Shared Memory not found\n";
        return 1;
    }

    SharedData* data = (SharedData*)MapViewOfFile(
        hMap,
        FILE_MAP_ALL_ACCESS,
        0, 0,
        sizeof(SharedData)
    );

    while (true) {

        data->vel_x += data->acc_x;
        data->vel_y += data->acc_y;

        data->x += data->vel_x;
        data->y += data->vel_y;

    
        if (data->x < 0) {
            data->x = 1;
            data->vel_x *= -1;
        }
        if (data->x > 1720) {
            data->x = 1719;
            data->vel_x *= -1;
        }

        if (data->y < -200) {
            data->y = 1000;
        }
        if (data->y > 1030) {
            data->y = 1029;
            data->vel_y *= -1;
        }

        Sleep(10);
    }

    return 0;
}