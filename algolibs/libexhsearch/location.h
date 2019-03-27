#pragma once
#include <iostream> 

namespace graph {

class Location {
public:
    using IndexType = int16_t;
    struct OffsetType {
        explicit OffsetType(int row, int column) noexcept : rowOffset(row), columnOffset(column) {}
        int rowOffset{ 0 };
        int columnOffset{ 0 };

        template <typename T>
        const OffsetType operator*(T scalar) { 
            return OffsetType(static_cast<int>(rowOffset * scalar), static_cast<int>(columnOffset * scalar)); 
        }
    };

    template <typename T, typename U>
    explicit Location(T row, U column) noexcept : row_(static_cast<IndexType>(row)), column_(static_cast<IndexType>(column)) {}

    const Location operator+(const OffsetType & offset) const noexcept;
    const Location & operator+=(const OffsetType & offset) noexcept;

    bool operator==(const Location & rhs) const noexcept;
    bool operator!=(const Location & rhs) const noexcept;
    bool operator<(const Location & rhs) const noexcept;

    IndexType getRow() const noexcept {
        return row_;
    }

    IndexType getColumn() const noexcept {
        return column_;
    }

private:
    IndexType row_{ 0 };
    IndexType column_{ 0 };
};

} // namespace graph

namespace std {
std::ostream & operator<<(std::ostream & stream, const graph::Location & location);
} // namespace std