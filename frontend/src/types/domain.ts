export type Course = {
  id: number;
  name: string;
};

export type Program = {
  id: number;
  name: string;
  department_id: number;
  subjects: Course[];
};

export type Department = {
  id: number;
  name: string;
  programs: Program[];
};

export type User = {
  id: number;
  name: string;
  email: string;
  unipd_id?: string | null;
};

export type ListingImage = {
  id: number;
  image_url: string;
};

export type Listing = {
  id: number;
  title: string;
  price: number;
  condition: string;
  description?: string | null;
  subject_id?: number | null;
  seller_id: number;
  seller: User;
  images: ListingImage[];
  created_at: string;
};
