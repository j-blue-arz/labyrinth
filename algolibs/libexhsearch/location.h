#pragma once
#include <iostream> 

namespace graph {

class Location {
public:
    struct OffsetType {
        explicit OffsetType(int row, int column) noexcept : rowOffset(row), columnOffset(column) {}
        int rowOffset{ 0 };
        int columnOffset{ 0 };
    };

    explicit Location(int row, int column) noexcept;

    const Location operator+(const OffsetType & offset) const noexcept;
    const Location & operator+=(const OffsetType & offset) noexcept;

    bool operator==(const Location & rhs) const noexcept;
    bool operator!=(const Location & rhs) const noexcept;
    bool operator<(const Location & rhs) const noexcept;

    int getRow() const noexcept;
    int getColumn() const noexcept;
private:
    int row_{ 0 };
    int column_{ 0 };
};

} // namespace graph

namespace std {
std::ostream & operator<<(std::ostream & stream, const graph::Location & location);
} // namespace std