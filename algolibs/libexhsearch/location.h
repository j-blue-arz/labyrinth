#pragma once

namespace graph {

	class Location {
	public:
		struct OffsetType {
			explicit OffsetType(int row, int column) : rowOffset(row), columnOffset(column) {}
			int rowOffset{ 0 };
			int columnOffset{ 0 };
		};

		explicit Location(int row, int column);

		const Location operator+(const OffsetType & offset) const;
		const Location & operator+=(const OffsetType & offset);

		bool operator==(const Location & rhs) const;
		bool operator!=(const Location & rhs) const;
		bool operator<(const Location & rhs) const;

		int getRow() const;
		int getColumn() const;
	private:
		int row_{ 0 };
		int column_{ 0 };
	};

}