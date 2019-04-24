#pragma once
#include <iostream> 

namespace graph {

class Location {
public:
    using IndexType = int16_t;
    struct OffsetType {
        using OffsetValueType = int;
        explicit OffsetType(OffsetValueType row, OffsetValueType column) noexcept : row_offset(row), column_offset(column) {}
        OffsetValueType row_offset{ 0 };
        OffsetValueType column_offset{ 0 };

        template <typename T>
        const OffsetType operator*(T scalar) { 
            return OffsetType(static_cast<int>(row_offset * scalar), static_cast<int>(column_offset * scalar)); 
        }
    };

    template <typename T, typename U>
    explicit Location(T row, U column) noexcept : row_(static_cast<IndexType>(row)), column_(static_cast<IndexType>(column)) {}
    virtual ~Location() = default;
    Location(const Location&) = default;
    Location& operator=(const Location&) = default;
    Location(Location&&) = default;
    Location& operator=(Location&&) = default;

    const Location operator+(const OffsetType & offset) const noexcept;
    const Location & operator+=(const OffsetType & offset) noexcept;

    IndexType getRow() const noexcept {
        return row_;
    }

    IndexType getColumn() const noexcept {
        return column_;
    }

protected:
    IndexType row_{ 0 };
    IndexType column_{ 0 };
};

inline bool operator==(const graph::Location & lhs, const graph::Location & rhs) {
    return lhs.getRow() == rhs.getRow() && lhs.getColumn() == rhs.getColumn();
}

inline bool operator!=(const graph::Location & lhs, const graph::Location & rhs) noexcept {
    return !(lhs == rhs);
}

inline bool operator<(const graph::Location & lhs, const graph::Location & rhs) noexcept {
    if(lhs.getRow() < rhs.getRow()) return true;
    if(lhs.getRow() > rhs.getRow()) return false;
    return lhs.getColumn() < rhs.getColumn();
}

} // namespace graph

namespace std {
std::ostream & operator<<(std::ostream & stream, const graph::Location & location);

template<> struct hash<graph::Location> {
    std::size_t operator()(graph::Location const& location) const noexcept {
        std::size_t const row_hash{std::hash<std::size_t>{}(location.getRow())};
        std::size_t const column_hash{std::hash<std::size_t>{}(location.getColumn())};
        return row_hash ^ (column_hash << 1);
    }
};

} // namespace std