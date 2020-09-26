#include "location.h"

namespace labyrinth {

const Location Location::operator+(const OffsetType& offset) const noexcept {
    return Location{row_ + offset.row_offset, column_ + offset.column_offset};
}

const Location& Location::operator+=(const OffsetType& offset) noexcept {
    row_ += offset.row_offset;
    column_ += offset.column_offset;
    return *this;
}

} // namespace labyrinth

namespace std {
std::ostream& operator<<(std::ostream& stream, const labyrinth::Location& location) {
    stream << "(" << location.getRow() << ", " << location.getColumn() << ")";
    return stream;
}
} // namespace std
