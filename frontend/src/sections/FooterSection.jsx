const FooterSection = () => {
  return (
    <section style={{ backgroundColor: '#9CFB4B' }} className="py-3">
      <div className="max-w-7xl mx-auto px-5 md:px-10">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-black text-sm">
          <p className="font-bold">Made by team GitGoneWild - Redact 2025</p>
          <div className="flex items-center gap-7">
            <p className="cursor-pointer hover:text-gray-800 font-bold">Privacy Policy</p>
            <p className="cursor-pointer hover:text-gray-800 font-bold">Terms of Service</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FooterSection;
