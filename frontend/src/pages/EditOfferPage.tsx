import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOffer, useUpdateOffer } from '@/hooks/useOffers';
import { useCommunity } from '@/contexts/CommunityContext';
import { useAuth } from '@/contexts/AuthContext';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
import { VisibilitySelector } from '@/components/VisibilitySelector';
import { RESOURCE_CATEGORIES, COMMON_UNITS, COMMON_LOCATIONS } from '@/utils/categories';
import { ArrowLeft } from 'lucide-react';

export function EditOfferPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: offer, isLoading: loadingOffer } = useOffer(id!);
  const updateOffer = useUpdateOffer();
  const { currentCommunity } = useCommunity();
  const { user, isAuthenticated, loading } = useAuth();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [item, setItem] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('kg');
  const [location, setLocation] = useState('');
  const [availableFrom, setAvailableFrom] = useState('');
  const [availableUntil, setAvailableUntil] = useState('');
  const [note, setNote] = useState('');
  const [visibility, setVisibility] = useState<'my_cell' | 'my_community' | 'trusted_network' | 'anyone_local' | 'network_wide'>('trusted_network');
  const [anonymous, setAnonymous] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  // Populate form when offer loads
  useEffect(() => {
    if (offer) {
      setTitle(offer.title || '');
      setDescription(offer.description || '');
      setItem(offer.resource_spec_id || '');
      setQuantity(offer.quantity?.toString() || '');
      setUnit(offer.unit || 'kg');
      setLocation(offer.location_id || '');
      setAvailableFrom(offer.available_from ? new Date(offer.available_from).toISOString().split('T')[0] : '');
      setAvailableUntil(offer.available_until ? new Date(offer.available_until).toISOString().split('T')[0] : '');
      setNote(offer.description || '');
      setVisibility((offer.visibility as any) || 'trusted_network');
      setAnonymous(offer.anonymous || false);
    }
  }, [offer]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login?redirect=/offers');
    }
  }, [loading, isAuthenticated, navigate]);

  // Don't render if not authenticated or not the owner
  if (loading || loadingOffer) {
    return <div className="max-w-2xl mx-auto p-8 text-center">Loading...</div>;
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  if (!offer) {
    return (
      <div className="max-w-2xl mx-auto p-8 text-center">
        <ErrorMessage message="Offer not found" />
        <Button onClick={() => navigate('/offers')} className="mt-4">
          Back to Offers
        </Button>
      </div>
    );
  }

  // Check ownership (if not anonymous)
  if (!offer.anonymous && offer.agent_id !== user.id) {
    return (
      <div className="max-w-2xl mx-auto p-8 text-center">
        <ErrorMessage message="You can only edit your own offers" />
        <Button onClick={() => navigate('/offers')} className="mt-4">
          Back to Offers
        </Button>
      </div>
    );
  }

  const selectedCategory = RESOURCE_CATEGORIES.find(cat => cat.id === category);
  const subcategories = selectedCategory?.subcategories || [];
  const selectedSubcategory = subcategories.find(sub => sub.id === subcategory);
  const items = selectedSubcategory?.items || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);

    const resourceName = item || title || `${category}/${subcategory}`;

    if (!resourceName || !quantity) {
      setErrors(['Please provide a resource name and quantity']);
      return;
    }

    // Validate date range
    if (availableFrom && availableUntil) {
      const fromDate = new Date(availableFrom);
      const untilDate = new Date(availableUntil);

      if (untilDate <= fromDate) {
        setErrors(['"Available Until" must be after "Available From"']);
        return;
      }
    }

    try {
      await updateOffer.mutateAsync({
        id: id!,
        data: {
          title: title || item,
          resource_spec_id: resourceName,
          quantity: parseFloat(quantity),
          unit,
          location_id: location || undefined,
          available_from: availableFrom || undefined,
          available_until: availableUntil || undefined,
          description: description || note || undefined,
          visibility,
        },
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/offers');
      }, 1500);
    } catch (error) {
      setErrors(['Failed to update offer. Please try again.']);
    }
  };

  if (success) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="confirmation success-message bg-green-50 border-l-4 border-green-500 p-6 rounded-lg">
          <h2 className="text-2xl font-bold text-green-900 mb-2">✓ Offer Updated!</h2>
          <p className="text-green-700 mb-4">Your offer has been updated successfully!</p>
          <p className="text-sm text-gray-600 mt-4">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Edit Offer</h1>
        <p className="text-gray-600 mt-1">Update your offer details</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {errors.length > 0 && (
            <ErrorMessage message={errors.join(', ')} />
          )}

          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">What are you offering?</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Title *
              </label>
              <input
                type="text"
                name="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Fresh Tomatoes, Bicycle Repair Skills"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Resource Type
              </label>
              <select
                name="resource_spec"
                value={item}
                onChange={(e) => setItem(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
              >
                <option value="">Select type (optional)...</option>
                <option value="Tomatoes">Tomatoes</option>
                <option value="Tools">Tools</option>
                <option value="Skills">Skills</option>
                <option value="Seeds">Seeds</option>
                <option value="Materials">Materials</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                name="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                placeholder="Tell us more about what you're offering..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity *
              </label>
              <input
                type="number"
                name="quantity"
                step="0.01"
                min="0"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unit *
              </label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
                required
              >
                {COMMON_UNITS.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
            >
              <option value="">No specific location</option>
              {COMMON_LOCATIONS.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available From
              </label>
              <input
                type="date"
                value={availableFrom}
                onChange={(e) => setAvailableFrom(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Until
              </label>
              <input
                type="date"
                value={availableUntil}
                onChange={(e) => setAvailableUntil(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-solarpunk-500 focus:border-solarpunk-500"
              />
            </div>
          </div>

          <VisibilitySelector
            value={visibility}
            onChange={(val) => setVisibility(val as any)}
          />

          {anonymous && (
            <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> This is an anonymous gift. You cannot change the anonymous status after creation.
              </p>
            </div>
          )}

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(-1)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateOffer.isPending}
              className="flex-1"
            >
              {updateOffer.isPending ? 'Updating...' : 'Update Offer'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
