#include "location.h"

namespace graph {

Location::Location(int row, int column) noexcept : row_(row), column_(column) {
}

const Location Location::operator+(const OffsetType & offset) const noexcept {
    return Location(row_ + offset.rowOffset, column_ + offset.columnOffset);
}

const Location & Location::operator+=(const OffsetType & offset) noexcept {
    row_ += offset.rowOffset;
    column_ += offset.columnOffset;
    return *this;
}

bool Location::operator==(const Location & rhs) const noexcept {
    return row_ == rhs.row_ && column_ == rhs.column_;
}

bool Location::operator!=(const Location & rhs) const noexcept {
    return !(*this == rhs);
}

bool Location::operator<(const Location & rhs) const noexcept {
    if (row_ < rhs.row_) return true;
    if (row_ > rhs.row_) return false;
    return column_ < rhs.column_;
}

int Location::getRow() const noexcept {
    return row_;
}

int Location::getColumn() const noexcept {
    return column_;
}

} // namespace graph

namespace std {
std::ostream & operator<<(std::ostream & stream, const graph::Location & location) {
    stream << "(" << location.getRow() << ", " << location.getColumn() << ")";
    return stream;
}
} // namespace std
